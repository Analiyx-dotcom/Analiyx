"""Dashboard summary stats for the user"""
from fastapi import APIRouter, Depends
from auth import get_current_user_id
from bson import ObjectId
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

db = None

def set_database(database):
    global db
    db = database

@router.get("/summary")
async def get_dashboard_summary(user_id: str = Depends(get_current_user_id)):
    """Get user's dashboard summary stats"""
    uid = ObjectId(user_id)
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    workspaces = await db.workspaces.count_documents({"user_id": uid})
    total_files = await db.uploaded_files.count_documents({"user_id": uid})
    recent_files = await db.uploaded_files.count_documents({"user_id": uid, "uploaded_at": {"$gte": week_ago}})
    ai_queries = await db.ai_searches.count_documents({"user_id": uid})
    ai_visibility = await db.ai_visibility.count_documents({"user_id": uid}) if await db.list_collection_names() and "ai_visibility" in await db.list_collection_names() else 0

    # Recent activity
    activities = []
    recent_uploads = await db.uploaded_files.find(
        {"user_id": uid}, {"_id": 0, "filename": 1, "uploaded_at": 1, "source_type": 1}
    ).sort("uploaded_at", -1).limit(5).to_list(5)
    for f in recent_uploads:
        activities.append({
            "type": "upload",
            "title": f"Uploaded {f['filename']}",
            "subtitle": f.get("source_type", "File"),
            "time": f["uploaded_at"].isoformat() if f.get("uploaded_at") else None
        })

    recent_ws = await db.workspaces.find(
        {"user_id": uid}, {"_id": 0, "name": 1, "created_at": 1, "data_sources": 1}
    ).sort("created_at", -1).limit(3).to_list(3)
    for ws in recent_ws:
        activities.append({
            "type": "workspace",
            "title": f"Created '{ws['name']}'",
            "subtitle": f"{len(ws.get('data_sources', []))} sources",
            "time": ws["created_at"].isoformat() if ws.get("created_at") else None
        })

    recent_searches = await db.ai_searches.find(
        {"user_id": uid}, {"_id": 0, "query": 1, "created_at": 1}
    ).sort("created_at", -1).limit(3).to_list(3)
    for s in recent_searches:
        activities.append({
            "type": "ai_search",
            "title": f"AI: \"{s['query'][:50]}\"",
            "subtitle": "AI Search",
            "time": s["created_at"].isoformat() if s.get("created_at") else None
        })

    # Sort by time desc
    activities.sort(key=lambda x: x.get("time") or "", reverse=True)

    return {
        "workspaces": workspaces,
        "total_files": total_files,
        "recent_files": recent_files,
        "ai_queries": ai_queries,
        "ai_visibility": ai_visibility,
        "activities": activities[:8]
    }
