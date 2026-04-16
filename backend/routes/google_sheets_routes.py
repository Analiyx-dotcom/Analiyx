"""
Google Sheets Routes — Dashboard data for connected Google Sheets.
Currently returns SAMPLE data. Developer needs to replace with actual Google Sheets API calls.
See API_CONTRACTS.md for the exact response schema.
"""
from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user_id
import random

router = APIRouter(prefix="/api/google-sheets", tags=["Google Sheets"])

db = None

def set_database(database):
    global db
    db = database


def _generate_sample_data():
    """Generate realistic sample Google Sheets data. Replace with actual Sheets API calls."""
    sheets = [
        {
            "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
            "title": "Monthly Sales Report",
            "last_modified": "2026-04-10T14:30:00Z",
            "sheet_count": 3,
            "row_count": 245,
            "preview_data": {
                "headers": ["Month", "Revenue", "Orders", "Avg Order Value", "Growth %"],
                "rows": [
                    ["Jan 2026", "₹4,52,000", "128", "₹3,531", "+12%"],
                    ["Feb 2026", "₹5,18,000", "145", "₹3,572", "+14.6%"],
                    ["Mar 2026", "₹4,89,000", "137", "₹3,569", "-5.6%"],
                    ["Apr 2026", "₹6,12,000", "168", "₹3,643", "+25.2%"],
                ],
            },
            "chart_data": [
                {"name": "Jan", "revenue": 452000, "orders": 128},
                {"name": "Feb", "revenue": 518000, "orders": 145},
                {"name": "Mar", "revenue": 489000, "orders": 137},
                {"name": "Apr", "revenue": 612000, "orders": 168},
                {"name": "May", "revenue": 575000, "orders": 155},
                {"name": "Jun", "revenue": 698000, "orders": 189},
            ],
        },
        {
            "spreadsheet_id": "2CyiNWt1YSB6oGNcLwCeekhmVVrqullct85PhWF3vqnt",
            "title": "Customer Feedback Tracker",
            "last_modified": "2026-04-12T09:15:00Z",
            "sheet_count": 2,
            "row_count": 89,
            "preview_data": {
                "headers": ["Date", "Customer", "Rating", "Category", "Status"],
                "rows": [
                    ["Apr 12", "Acme Corp", "4.5", "Product Quality", "Resolved"],
                    ["Apr 11", "Beta LLC", "3.0", "Support", "In Progress"],
                    ["Apr 10", "Gamma Inc", "5.0", "Delivery", "Resolved"],
                    ["Apr 09", "Delta Co", "2.5", "Pricing", "Open"],
                ],
            },
            "chart_data": [
                {"name": "Product Quality", "value": 35},
                {"name": "Support", "value": 28},
                {"name": "Delivery", "value": 18},
                {"name": "Pricing", "value": 12},
                {"name": "Other", "value": 7},
            ],
        },
    ]

    return {
        "is_sample_data": True,
        "total_sheets": len(sheets),
        "sheets": sheets,
    }


@router.get("/report")
async def get_sheets_report(user_id: str = Depends(get_current_user_id)):
    """
    Get connected Google Sheets data.
    TODO (Developer): Replace _generate_sample_data() with actual Google Sheets API call.
    Required: OAuth token, Spreadsheet IDs
    API: GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values/{range}
    """
    return _generate_sample_data()
