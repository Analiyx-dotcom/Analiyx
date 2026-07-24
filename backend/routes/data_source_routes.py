from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from auth import get_current_user_id
from datetime import datetime
from bson import ObjectId
import pandas as pd
import io
import json

router = APIRouter(prefix="/api/data-sources", tags=["Data Sources"])

# Database will be injected
db = None

def set_database(database):
    global db
    db = database

DATA_SOURCE_LIMITS = {
    "Starter": 4,
    "Business Pro": 999,
    "Enterprise": 999,
}

async def _is_trial_active(db, user_id):
    """Check if user's trial period is still active"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False
    trial_ends = user.get("trial_ends_at")
    if trial_ends and trial_ends > datetime.utcnow():
        return True
    return False

@router.get("/limits")
async def get_data_source_limits(user_id: str = Depends(get_current_user_id)):
    """Get data source limits and current usage for user"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = user.get("plan", "Starter")
    trial_active = user.get("trial_ends_at") and user["trial_ends_at"] > datetime.utcnow()
    limit = 999 if trial_active else DATA_SOURCE_LIMITS.get(plan, 4)
    
    file_count = await db.uploaded_files.count_documents({"user_id": ObjectId(user_id)})
    integration_count = await db.integrations.count_documents({"user_id": ObjectId(user_id), "status": "connected"})
    current = file_count + integration_count
    
    return {
        "plan": plan,
        "limit": limit,
        "current": current,
        "remaining": max(0, limit - current),
        "can_add": current < limit,
        "trial_active": bool(trial_active)
    }

@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    workspace_id: str = None
):
    """Upload and analyze CSV/Excel file"""
    from credits import check_and_deduct_credits
    
    # Check and deduct credits (2 credits per file upload)
    credit_result = await check_and_deduct_credits(db, user_id, "file_upload")
    
    # Check data source limit — skip during trial
    trial_active = await _is_trial_active(db, user_id)
    if not trial_active:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            plan = user.get("plan", "Starter")
            limit = DATA_SOURCE_LIMITS.get(plan, 4)
            file_count = await db.uploaded_files.count_documents({"user_id": ObjectId(user_id)})
            integration_count = await db.integrations.count_documents({"user_id": ObjectId(user_id), "status": "connected"})
            if (file_count + integration_count) >= limit:
                raise HTTPException(
                    status_code=403,
                    detail=f"DATA_SOURCE_LIMIT_REACHED: Your {plan} plan allows {limit} data source connections. Upgrade to Business Pro for unlimited connections."
                )
    
    # Validate file type
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_ext = '.' + file.filename.split('.')[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only CSV and Excel files are allowed."
        )
    
    try:
        # Read file content
        contents = await file.read()
        
        # Parse file based on type
        if file_ext == '.csv':
            df = pd.read_csv(io.BytesIO(contents))
        else:  # Excel files
            df = pd.read_excel(io.BytesIO(contents))
        
        # Generate basic analytics
        analytics = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "missing_values": {k: int(v) for k, v in df.isnull().sum().to_dict().items()},
            "numeric_summary": {}
        }
        
        # Get summary statistics for numeric columns — sanitize NaN/Inf
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            summary = df[numeric_cols].describe().to_dict()
            clean_summary = {}
            for col, stats in summary.items():
                clean_summary[col] = {}
                for stat_name, val in stats.items():
                    if pd.isna(val) or (isinstance(val, float) and (val == float('inf') or val == float('-inf'))):
                        clean_summary[col][stat_name] = None
                    else:
                        clean_summary[col][stat_name] = round(float(val), 4) if isinstance(val, float) else val
            analytics["numeric_summary"] = clean_summary
        
        # Get sample data (first 5 rows) — sanitize NaN
        sample_df = df.head(5).fillna("")
        sample_data = json.loads(sample_df.to_json(orient='records', default_handler=str))
        
        # Semantic type detection + data quality (metadata engine)
        try:
            from services.metadata.semantic_types import detect_semantic_type
            from services.semantic.business_metrics import match_business_terms, BusinessMetricsService
            column_semantics = {}
            for col in df.columns:
                samples = df[col].dropna().astype(str).head(20).tolist()
                column_semantics[str(col)] = detect_semantic_type(str(col), str(df[col].dtype), samples)
            analytics["column_semantics"] = column_semantics
            duplicate_rows = int(df.duplicated().sum())
            analytics["duplicate_rows"] = duplicate_rows
            total_cells = max(len(df) * max(len(df.columns), 1), 1)
            missing_pct = sum(analytics["missing_values"].values()) / total_cells * 100
            dup_pct = duplicate_rows / max(len(df), 1) * 100
            analytics["quality_score"] = max(0, round(100 - min(missing_pct * 0.6, 40) - min(dup_pct * 0.5, 20), 1))
            business_terms = match_business_terms([str(c) for c in df.columns])
            analytics["business_terms"] = business_terms
            if business_terms:
                inferred = [{"metric": m, "schema": "", "table": file.filename, "columns": cols}
                            for m, cols in business_terms.items()]
                await BusinessMetricsService(db).seed_glossary(str(user_id), inferred)
        except Exception as meta_err:
            import logging
            logging.getLogger(__name__).warning("File metadata enrichment failed: %s", meta_err)
        
        # Store file metadata in database
        file_doc = {
            "user_id": ObjectId(user_id),
            "filename": file.filename,
            "file_type": file_ext,
            "source_type": "Excel" if file_ext in ['.xlsx', '.xls'] else "CSV",
            "analytics": analytics,
            "sample_data": sample_data,
            "uploaded_at": datetime.utcnow(),
            "status": "processed"
        }
        if workspace_id:
            file_doc["workspace_id"] = ObjectId(workspace_id)
        
        result = await db.uploaded_files.insert_one(file_doc)
        
        return {
            "success": True,
            "file_id": str(result.inserted_id),
            "filename": file.filename,
            "analytics": analytics,
            "sample_data": sample_data,
            "message": f"File processed successfully! Found {len(df)} rows and {len(df.columns)} columns."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/uploaded-files")
async def get_uploaded_files(user_id: str = Depends(get_current_user_id), workspace_id: str = None):
    """Get all uploaded files for current user, optionally filtered by workspace"""
    
    query = {"user_id": ObjectId(user_id)}
    if workspace_id:
        query["workspace_id"] = ObjectId(workspace_id)
    
    files_cursor = db.uploaded_files.find(query).sort("uploaded_at", -1)
    
    files = await files_cursor.to_list(length=100)
    
    formatted_files = []
    for file in files:
        formatted_files.append({
            "id": str(file["_id"]),
            "filename": file["filename"],
            "source_type": file["source_type"],
            "total_rows": file["analytics"]["total_rows"],
            "total_columns": file["analytics"]["total_columns"],
            "uploaded_at": file["uploaded_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "status": file["status"]
        })
    
    return {"files": formatted_files}

@router.get("/file-details/{file_id}")
async def get_file_details(
    file_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed analytics for a specific file"""
    
    file = await db.uploaded_files.find_one({
        "_id": ObjectId(file_id),
        "user_id": ObjectId(user_id)
    })
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "id": str(file["_id"]),
        "filename": file["filename"],
        "source_type": file["source_type"],
        "analytics": file["analytics"],
        "sample_data": file["sample_data"],
        "uploaded_at": file["uploaded_at"].strftime("%Y-%m-%d %H:%M:%S")
    }

@router.delete("/file/{file_id}")
async def delete_file(
    file_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete an uploaded file"""
    
    result = await db.uploaded_files.delete_one({
        "_id": ObjectId(file_id),
        "user_id": ObjectId(user_id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"success": True, "message": "File deleted successfully"}
