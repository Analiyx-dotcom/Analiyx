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

@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Upload and analyze CSV/Excel file"""
    
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
async def get_uploaded_files(user_id: str = Depends(get_current_user_id)):
    """Get all uploaded files for current user"""
    
    files_cursor = db.uploaded_files.find(
        {"user_id": ObjectId(user_id)}
    ).sort("uploaded_at", -1)
    
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
