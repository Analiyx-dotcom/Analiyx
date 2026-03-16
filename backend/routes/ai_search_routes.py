"""AI Search - Natural language query over user's uploaded data"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user_id
from bson import ObjectId
from datetime import datetime
import os
import json
import logging

router = APIRouter(prefix="/api/ai", tags=["AI Search"])

db = None

def set_database(database):
    global db
    db = database

class SearchQuery(BaseModel):
    query: str

@router.post("/search")
async def ai_search(req: SearchQuery, user_id: str = Depends(get_current_user_id)):
    """Search user's data using natural language powered by GPT-5.2"""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    # Gather user's data context
    files = await db.uploaded_files.find(
        {"user_id": ObjectId(user_id)},
        {"_id": 0, "filename": 1, "analysis_results": 1}
    ).to_list(20)

    workspaces = await db.workspaces.find(
        {"user_id": ObjectId(user_id)},
        {"_id": 0, "name": 1, "data_sources": 1}
    ).to_list(20)

    # Build context from user's data
    data_context = ""
    for f in files:
        data_context += f"\n--- File: {f['filename']} ---\n"
        ar = f.get("analysis_results", {})
        if ar.get("summary"):
            data_context += f"Summary: {json.dumps(ar['summary'])}\n"
        if ar.get("column_analysis"):
            cols = list(ar["column_analysis"].keys())
            data_context += f"Columns: {', '.join(cols)}\n"
        if ar.get("numeric_stats"):
            data_context += f"Stats: {json.dumps(ar['numeric_stats'])}\n"

    ws_context = ""
    for ws in workspaces:
        ws_context += f"Workspace '{ws['name']}': data sources = {', '.join(ws.get('data_sources', []))}\n"

    if not data_context and not ws_context:
        return {
            "answer": "You haven't uploaded any data yet. Upload CSV/Excel files or connect data sources to start querying with AI.",
            "sources": []
        }

    system_msg = (
        "You are Analiyx AI, a data analytics assistant. The user has uploaded data files and created workspaces. "
        "Answer their questions based on the data context provided. Be concise, specific, and actionable. "
        "If data is insufficient, suggest what additional data sources could help. "
        "Format numbers with commas and use INR (₹) for currency."
    )

    user_text = f"My data context:\n{data_context}\n{ws_context}\n\nQuestion: {req.query}"

    try:
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        chat = LlmChat(
            api_key=api_key,
            session_id=f"search_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}",
            system_message=system_msg
        ).with_model("openai", "gpt-5.2")

        response = await chat.send_message(UserMessage(text=user_text))

        # Log the search
        await db.ai_searches.insert_one({
            "user_id": ObjectId(user_id),
            "query": req.query,
            "response": response[:500],
            "created_at": datetime.utcnow()
        })

        sources = [f["filename"] for f in files]
        return {"answer": response, "sources": sources}
    except Exception as e:
        logging.error(f"AI Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI search failed: {str(e)}")
