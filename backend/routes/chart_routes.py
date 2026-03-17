"""Auto-generate chart configurations and notes/reports for user dashboards"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user_id
from bson import ObjectId
from datetime import datetime
from typing import Optional, List
import json
import logging

router = APIRouter(prefix="/api/charts", tags=["Charts"])

db = None

def set_database(database):
    global db
    db = database


@router.get("/generate/{file_id}")
async def generate_charts(file_id: str, user_id: str = Depends(get_current_user_id)):
    """Auto-generate chart configurations from uploaded file data"""
    file_doc = await db.uploaded_files.find_one(
        {"_id": ObjectId(file_id), "user_id": ObjectId(user_id)},
        {"_id": 0, "filename": 1, "analytics": 1, "sample_data": 1, "source_type": 1}
    )
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    analytics = file_doc.get("analytics", {})
    sample_data = file_doc.get("sample_data", [])
    columns = analytics.get("columns", [])
    data_types = analytics.get("data_types", {})
    numeric_summary = analytics.get("numeric_summary", {})
    total_rows = analytics.get("total_rows", 0)
    total_columns = analytics.get("total_columns", 0)

    # Classify columns
    numeric_cols = [c for c in columns if data_types.get(c) in ("int64", "float64", "int32", "float32", "number")]
    text_cols = [c for c in columns if data_types.get(c) in ("object", "str", "string", "category")]
    date_cols = [c for c in columns if "date" in c.lower() or "time" in c.lower() or data_types.get(c) in ("datetime64[ns]", "datetime")]

    charts = []

    # KPI Cards
    kpis = [
        {"label": "Total Rows", "value": total_rows, "format": "number"},
        {"label": "Columns", "value": total_columns, "format": "number"},
        {"label": "Data Type", "value": file_doc.get("source_type", "File"), "format": "text"},
    ]
    for nc in numeric_cols[:2]:
        stats = numeric_summary.get(nc, {})
        if stats.get("mean") is not None:
            kpis.append({"label": f"Avg {nc}", "value": round(stats["mean"], 2), "format": "number"})
        if stats.get("sum") is not None:
            kpis.append({"label": f"Total {nc}", "value": round(stats["sum"], 2), "format": "number"})
    charts.append({"type": "kpi", "title": "Key Metrics", "data": kpis[:6]})

    # Bar Chart - numeric columns comparison
    if numeric_cols and sample_data:
        bar_col = numeric_cols[0]
        label_col = text_cols[0] if text_cols else columns[0] if columns else None
        if label_col and label_col != bar_col:
            bar_data = []
            for row in sample_data[:15]:
                val = row.get(bar_col)
                try:
                    val = float(val) if val is not None else 0
                except (ValueError, TypeError):
                    val = 0
                bar_data.append({"name": str(row.get(label_col, ""))[:20], "value": val})
            if bar_data:
                charts.append({"type": "bar", "title": f"{bar_col} by {label_col}", "data": bar_data, "dataKey": "value", "nameKey": "name", "color": "#8b5cf6"})

    # Line Chart - if there's a numeric trend
    if len(numeric_cols) >= 1 and sample_data:
        line_col = numeric_cols[0]
        line_data = []
        for idx, row in enumerate(sample_data[:20]):
            val = row.get(line_col)
            try:
                val = float(val) if val is not None else 0
            except (ValueError, TypeError):
                val = 0
            label = str(row.get(date_cols[0] if date_cols else text_cols[0] if text_cols else "", f"#{idx+1}"))[:15]
            line_data.append({"name": label, "value": val})
        if line_data:
            charts.append({"type": "line", "title": f"{line_col} Trend", "data": line_data, "dataKey": "value", "color": "#06b6d4"})

    # Donut Chart - data type distribution
    type_counts = {}
    for col in columns:
        t = data_types.get(col, "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    donut_data = [{"name": k, "value": v} for k, v in type_counts.items()]
    if donut_data:
        charts.append({"type": "donut", "title": "Data Type Distribution", "data": donut_data, "colors": ["#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]})

    # Category distribution donut (if text column exists)
    if text_cols and sample_data:
        cat_col = text_cols[0]
        cat_counts = {}
        for row in sample_data:
            val = str(row.get(cat_col, ""))
            if val:
                cat_counts[val] = cat_counts.get(val, 0) + 1
        cat_donut = [{"name": k[:20], "value": v} for k, v in sorted(cat_counts.items(), key=lambda x: -x[1])[:8]]
        if cat_donut and len(cat_donut) > 1:
            charts.append({"type": "donut", "title": f"{cat_col} Distribution", "data": cat_donut, "colors": ["#8b5cf6", "#ec4899", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#6366f1", "#14b8a6"]})

    # Table - sample data
    if sample_data:
        charts.append({"type": "table", "title": "Sample Data", "data": sample_data[:10], "columns": columns[:8]})

    # Numeric stats table
    if numeric_summary:
        stats_rows = []
        for col, stats in numeric_summary.items():
            stats_rows.append({
                "Column": col,
                "Min": round(stats.get("min", 0), 2) if isinstance(stats.get("min"), (int, float)) else str(stats.get("min", "")),
                "Max": round(stats.get("max", 0), 2) if isinstance(stats.get("max"), (int, float)) else str(stats.get("max", "")),
                "Mean": round(stats.get("mean", 0), 2) if isinstance(stats.get("mean"), (int, float)) else str(stats.get("mean", "")),
                "Std": round(stats.get("std", 0), 2) if isinstance(stats.get("std"), (int, float)) else str(stats.get("std", "")),
            })
        if stats_rows:
            charts.append({"type": "table", "title": "Numeric Statistics", "data": stats_rows, "columns": ["Column", "Min", "Max", "Mean", "Std"]})

    return {"filename": file_doc["filename"], "charts": charts}


# --- Notes ---
class NoteCreate(BaseModel):
    title: str
    content: str
    workspace_id: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

@router.post("/notes")
async def create_note(note: NoteCreate, user_id: str = Depends(get_current_user_id)):
    doc = {
        "user_id": ObjectId(user_id),
        "title": note.title,
        "content": note.content,
        "workspace_id": ObjectId(note.workspace_id) if note.workspace_id else None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.notes.insert_one(doc)
    return {"id": str(result.inserted_id), "title": note.title}

@router.get("/notes")
async def get_notes(user_id: str = Depends(get_current_user_id)):
    notes = await db.notes.find({"user_id": ObjectId(user_id)}).sort("updated_at", -1).to_list(50)
    return {"notes": [{"id": str(n["_id"]), "title": n["title"], "content": n["content"], "workspace_id": str(n["workspace_id"]) if n.get("workspace_id") else None, "created_at": n["created_at"].isoformat(), "updated_at": n["updated_at"].isoformat()} for n in notes]}

@router.put("/notes/{note_id}")
async def update_note(note_id: str, note: NoteUpdate, user_id: str = Depends(get_current_user_id)):
    updates = {"updated_at": datetime.utcnow()}
    if note.title is not None:
        updates["title"] = note.title
    if note.content is not None:
        updates["content"] = note.content
    result = await db.notes.update_one({"_id": ObjectId(note_id), "user_id": ObjectId(user_id)}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"success": True}

@router.delete("/notes/{note_id}")
async def delete_note(note_id: str, user_id: str = Depends(get_current_user_id)):
    result = await db.notes.delete_one({"_id": ObjectId(note_id), "user_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"success": True}


# --- Reports ---
@router.get("/reports")
async def get_reports(user_id: str = Depends(get_current_user_id)):
    """Get all generated reports for user"""
    files = await db.uploaded_files.find(
        {"user_id": ObjectId(user_id)},
        {"_id": 1, "filename": 1, "source_type": 1, "uploaded_at": 1, "analytics": 1}
    ).sort("uploaded_at", -1).to_list(50)

    reports = []
    for f in files:
        analytics = f.get("analytics", {})
        reports.append({
            "id": str(f["_id"]),
            "filename": f["filename"],
            "source_type": f.get("source_type", "File"),
            "uploaded_at": f["uploaded_at"].isoformat() if f.get("uploaded_at") else None,
            "total_rows": analytics.get("total_rows", 0),
            "total_columns": analytics.get("total_columns", 0),
            "has_charts": True,
        })
    return {"reports": reports}
