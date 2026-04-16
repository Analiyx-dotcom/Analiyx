"""
Zoho Routes — Dashboard data for Zoho Books & CRM.
Currently returns SAMPLE data. Developer needs to replace with actual Zoho API calls.
See API_CONTRACTS.md for the exact response schema.
"""
from fastapi import APIRouter, Depends
from auth import get_current_user_id
from datetime import datetime, timezone, timedelta
import random

router = APIRouter(prefix="/api/zoho", tags=["Zoho"])

db = None

def set_database(database):
    global db
    db = database


def _generate_sample_books_data():
    """Generate realistic Zoho Books data. Replace with actual Zoho Books API calls."""
    months = []
    for i in range(6, 0, -1):
        d = datetime.now(timezone.utc) - timedelta(days=i * 30)
        income = round(random.uniform(350000, 750000), 2)
        expenses = round(income * random.uniform(0.55, 0.75), 2)
        months.append({
            "month": d.strftime("%b %Y"),
            "income": income,
            "expenses": expenses,
            "profit": round(income - expenses, 2),
        })

    invoices = [
        {"invoice_id": "INV-2026-0412", "customer": "TechFlow Solutions", "amount": 85000, "status": "paid", "due_date": "2026-04-20", "issue_date": "2026-03-20"},
        {"invoice_id": "INV-2026-0398", "customer": "GreenLeaf Organics", "amount": 42500, "status": "overdue", "due_date": "2026-04-05", "issue_date": "2026-03-05"},
        {"invoice_id": "INV-2026-0385", "customer": "UrbanCraft Studios", "amount": 126000, "status": "paid", "due_date": "2026-04-15", "issue_date": "2026-03-15"},
        {"invoice_id": "INV-2026-0371", "customer": "ByteForge Labs", "amount": 67800, "status": "sent", "due_date": "2026-04-25", "issue_date": "2026-03-25"},
        {"invoice_id": "INV-2026-0364", "customer": "SpiceRoute Exports", "amount": 198500, "status": "paid", "due_date": "2026-04-10", "issue_date": "2026-03-10"},
        {"invoice_id": "INV-2026-0350", "customer": "CloudNine Digital", "amount": 54200, "status": "draft", "due_date": "2026-04-30", "issue_date": "2026-04-01"},
    ]

    expense_categories = [
        {"category": "Salaries & Wages", "amount": 285000, "percentage": 38},
        {"category": "Marketing & Ads", "amount": 112000, "percentage": 15},
        {"category": "Office & Rent", "amount": 89500, "percentage": 12},
        {"category": "Software & Tools", "amount": 67000, "percentage": 9},
        {"category": "Travel & Transport", "amount": 45000, "percentage": 6},
        {"category": "Professional Services", "amount": 38000, "percentage": 5},
        {"category": "Other", "amount": 112500, "percentage": 15},
    ]

    total_income = sum(m["income"] for m in months)
    total_expenses = sum(m["expenses"] for m in months)
    total_invoiced = sum(inv["amount"] for inv in invoices)
    paid_invoices = sum(inv["amount"] for inv in invoices if inv["status"] == "paid")
    overdue_invoices = sum(inv["amount"] for inv in invoices if inv["status"] == "overdue")

    return {
        "is_sample_data": True,
        "module": "books",
        "summary": {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(total_income - total_expenses, 2),
            "profit_margin": round((total_income - total_expenses) / total_income * 100, 1) if total_income else 0,
            "total_invoiced": total_invoiced,
            "paid_invoices": paid_invoices,
            "overdue_amount": overdue_invoices,
            "accounts_receivable": total_invoiced - paid_invoices,
        },
        "monthly_performance": months,
        "invoices": invoices,
        "expense_categories": expense_categories,
    }


def _generate_sample_crm_data():
    """Generate realistic Zoho CRM data. Replace with actual Zoho CRM API calls."""
    pipeline_stages = [
        {"stage": "Qualification", "deals": 24, "value": 1850000},
        {"stage": "Needs Analysis", "deals": 18, "value": 2420000},
        {"stage": "Proposal", "deals": 12, "value": 3150000},
        {"stage": "Negotiation", "deals": 8, "value": 2890000},
        {"stage": "Closed Won", "deals": 15, "value": 4520000},
        {"stage": "Closed Lost", "deals": 6, "value": 980000},
    ]

    recent_deals = [
        {"deal_name": "Enterprise License - TechFlow", "stage": "Negotiation", "amount": 450000, "probability": 75, "close_date": "2026-04-30", "owner": "Anil K."},
        {"deal_name": "Annual Subscription - GreenLeaf", "stage": "Proposal", "amount": 180000, "probability": 50, "close_date": "2026-05-15", "owner": "Sonia M."},
        {"deal_name": "Custom Integration - ByteForge", "stage": "Closed Won", "amount": 320000, "probability": 100, "close_date": "2026-04-10", "owner": "Anil K."},
        {"deal_name": "Starter Plan - CloudNine", "stage": "Qualification", "amount": 85000, "probability": 20, "close_date": "2026-06-01", "owner": "Ravi P."},
        {"deal_name": "Upgrade - SpiceRoute", "stage": "Needs Analysis", "amount": 210000, "probability": 40, "close_date": "2026-05-20", "owner": "Sonia M."},
    ]

    monthly_deals = [
        {"month": "Nov", "won": 8, "lost": 3, "value_won": 2100000},
        {"month": "Dec", "won": 11, "lost": 4, "value_won": 3450000},
        {"month": "Jan", "won": 9, "lost": 2, "value_won": 2680000},
        {"month": "Feb", "won": 14, "lost": 5, "value_won": 4120000},
        {"month": "Mar", "won": 12, "lost": 3, "value_won": 3850000},
        {"month": "Apr", "won": 15, "lost": 6, "value_won": 4520000},
    ]

    lead_sources = [
        {"source": "Website", "leads": 145, "percentage": 32},
        {"source": "Referral", "leads": 98, "percentage": 22},
        {"source": "LinkedIn", "leads": 76, "percentage": 17},
        {"source": "Cold Outreach", "leads": 54, "percentage": 12},
        {"source": "Events", "leads": 42, "percentage": 9},
        {"source": "Other", "leads": 36, "percentage": 8},
    ]

    total_pipeline = sum(s["value"] for s in pipeline_stages if s["stage"] not in ["Closed Won", "Closed Lost"])
    total_won = sum(s["value"] for s in pipeline_stages if s["stage"] == "Closed Won")
    win_rate = round(15 / (15 + 6) * 100, 1)

    return {
        "is_sample_data": True,
        "module": "crm",
        "summary": {
            "total_pipeline_value": total_pipeline,
            "total_deals_won": total_won,
            "active_deals": sum(s["deals"] for s in pipeline_stages if s["stage"] not in ["Closed Won", "Closed Lost"]),
            "win_rate": win_rate,
            "avg_deal_size": round(total_won / 15, 2),
            "total_leads": sum(l["leads"] for l in lead_sources),
        },
        "pipeline_stages": pipeline_stages,
        "recent_deals": recent_deals,
        "monthly_deals": monthly_deals,
        "lead_sources": lead_sources,
    }


@router.get("/books/report")
async def get_zoho_books_report(user_id: str = Depends(get_current_user_id)):
    """
    Get Zoho Books financial report.
    TODO (Developer): Replace _generate_sample_books_data() with actual Zoho Books API calls.
    Required: Zoho OAuth Token, Organization ID
    API: GET https://www.zohoapis.com/books/v3/invoices?organization_id={org_id}
    Docs: https://www.zoho.com/books/api/v3/
    """
    return _generate_sample_books_data()


@router.get("/crm/report")
async def get_zoho_crm_report(user_id: str = Depends(get_current_user_id)):
    """
    Get Zoho CRM pipeline and deals report.
    TODO (Developer): Replace _generate_sample_crm_data() with actual Zoho CRM API calls.
    Required: Zoho OAuth Token
    API: GET https://www.zohoapis.com/crm/v6/Deals
    Docs: https://www.zoho.com/crm/developer/docs/api/v6/
    """
    return _generate_sample_crm_data()
