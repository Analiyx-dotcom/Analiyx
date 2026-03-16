"""AI Chat - Interactive multi-turn conversation over user's data"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user_id
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import os
import json
import logging

router = APIRouter(prefix="/api/ai", tags=["AI Chat"])

db = None

def set_database(database):
    global db
    db = database

class ChatMessage(BaseModel):
    query: str
    workspace_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatHistoryItem(BaseModel):
    role: str
    content: str
    timestamp: str = None

@router.post("/chat")
async def ai_chat(req: ChatMessage, user_id: str = Depends(get_current_user_id)):
    """Interactive multi-turn AI chat scoped to workspace data"""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    # Build session_id for conversation continuity
    ws_part = req.workspace_id or "global"
    session_id = req.session_id or f"chat_{user_id}_{ws_part}"

    # Gather workspace data context
    file_query = {"user_id": ObjectId(user_id)}
    if req.workspace_id:
        file_query["workspace_id"] = ObjectId(req.workspace_id)

    files = await db.uploaded_files.find(
        file_query,
        {"_id": 0, "filename": 1, "analysis_results": 1, "analytics": 1, "sample_data": 1}
    ).to_list(20)

    ws_query = {"user_id": ObjectId(user_id)}
    if req.workspace_id:
        ws_query["_id"] = ObjectId(req.workspace_id)

    workspaces = await db.workspaces.find(
        ws_query, {"_id": 0, "name": 1, "data_sources": 1}
    ).to_list(20)

    # Build rich data context
    data_context = ""
    for f in files:
        data_context += f"\n--- File: {f['filename']} ---\n"
        ar = f.get("analysis_results") or f.get("analytics") or {}
        if ar.get("summary"):
            data_context += f"Summary: {json.dumps(ar['summary'])}\n"
        if ar.get("columns"):
            data_context += f"Columns: {', '.join(ar['columns'])}\n"
        if ar.get("column_analysis"):
            data_context += f"Columns: {', '.join(ar['column_analysis'].keys())}\n"
        if ar.get("data_types"):
            data_context += f"Data Types: {json.dumps(ar['data_types'])}\n"
        if ar.get("numeric_stats") or ar.get("numeric_summary"):
            stats = ar.get("numeric_stats") or ar.get("numeric_summary")
            data_context += f"Numeric Stats: {json.dumps(stats)}\n"
        if ar.get("missing_values"):
            data_context += f"Missing Values: {json.dumps(ar['missing_values'])}\n"
        # Include sample data for deeper analysis
        sample = f.get("sample_data") or ar.get("sample_data")
        if sample and len(sample) > 0:
            data_context += f"Sample Data (first {len(sample)} rows): {json.dumps(sample[:5])}\n"

    ws_context = ""
    for ws in workspaces:
        ws_context += f"Workspace '{ws['name']}': sources = {', '.join(ws.get('data_sources', []))}\n"

    if not data_context and not ws_context:
        return {
            "answer": "No data uploaded yet. Upload CSV/Excel files to this workspace, then ask me anything about your data!",
            "sources": [],
            "session_id": session_id
        }

    system_msg = (
        "You are Analiyx AI, an expert data analytics assistant. You are having an interactive conversation "
        "with a user about their uploaded data. The user's data context is provided below.\n\n"
        "RULES:\n"
        "- Remember the full conversation history. Refer back to previous questions and answers.\n"
        "- Be conversational, helpful, and specific to the data.\n"
        "- When asked for analysis, provide concrete numbers, percentages, and actionable insights.\n"
        "- If user asks follow-up questions, build on previous context.\n"
        "- Format responses with markdown: use **bold**, bullet points, and headers for readability.\n"
        "- Use INR (₹) for currency values.\n"
        "- If data is insufficient for a question, say what's missing and suggest what to upload.\n\n"
        f"USER'S DATA:\n{data_context}\n{ws_context}"
    )

    try:
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_msg
        ).with_model("openai", "gpt-5.2")

        response = await chat.send_message(UserMessage(text=req.query))

        # Log the chat message
        await db.ai_searches.insert_one({
            "user_id": ObjectId(user_id),
            "workspace_id": ObjectId(req.workspace_id) if req.workspace_id else None,
            "session_id": session_id,
            "query": req.query,
            "response": response[:1000],
            "created_at": datetime.utcnow()
        })

        sources = [f["filename"] for f in files]
        return {"answer": response, "sources": sources, "session_id": session_id}
    except Exception as e:
        logging.error(f"AI Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI chat failed: {str(e)}")


# Keep the old search endpoint for backward compatibility
class SearchQuery(BaseModel):
    query: str
    workspace_id: Optional[str] = None

@router.post("/search")
async def ai_search(req: SearchQuery, user_id: str = Depends(get_current_user_id)):
    """Legacy single-query search - redirects to chat"""
    chat_req = ChatMessage(query=req.query, workspace_id=req.workspace_id)
    return await ai_chat(chat_req, user_id)


@router.get("/chat/history/{workspace_id}")
async def get_chat_history(workspace_id: str, user_id: str = Depends(get_current_user_id)):
    """Get recent chat history for a workspace"""
    messages = await db.ai_searches.find(
        {"user_id": ObjectId(user_id), "workspace_id": ObjectId(workspace_id)},
        {"_id": 0, "query": 1, "response": 1, "created_at": 1}
    ).sort("created_at", -1).limit(20).to_list(20)

    history = []
    for m in reversed(messages):
        history.append({"role": "user", "content": m["query"], "timestamp": m["created_at"].isoformat()})
        history.append({"role": "assistant", "content": m["response"], "timestamp": m["created_at"].isoformat()})

    return {"history": history}
