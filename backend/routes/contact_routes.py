"""Contact form and support ticket routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

router = APIRouter(prefix="/api", tags=["Contact"])

db = None

def set_database(database):
    global db
    db = database

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    company: str = ""
    phone: str = ""
    message: str

NOTIFICATION_EMAIL = "analiyx26@gmail.com"

@router.post("/contact")
async def submit_contact_form(form: ContactForm):
    """Submit contact form and store in DB, send email notification"""
    contact_doc = {
        "name": form.name,
        "email": form.email,
        "company": form.company,
        "phone": form.phone,
        "message": form.message,
        "status": "new",
        "created_at": datetime.utcnow()
    }
    await db.contact_submissions.insert_one(contact_doc)

    # Send email notification
    try:
        from email_service import send_email
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#1a1a2e;color:#fff;padding:30px;border-radius:12px;">
            <h2 style="color:#a855f7;">New Contact Form Submission</h2>
            <div style="background:#16213e;padding:15px;border-radius:8px;margin:15px 0;">
                <p><strong>Name:</strong> {form.name}</p>
                <p><strong>Email:</strong> {form.email}</p>
                <p><strong>Company:</strong> {form.company or 'N/A'}</p>
                <p><strong>Phone:</strong> {form.phone or 'N/A'}</p>
            </div>
            <div style="background:#16213e;padding:15px;border-radius:8px;">
                <p><strong>Message:</strong></p>
                <p style="color:#e2e8f0;">{form.message}</p>
            </div>
        </div>
        """
        send_email(NOTIFICATION_EMAIL, f"[Analiyx Contact] {form.name} - {form.company or 'N/A'}", html)
    except Exception as e:
        logging.warning(f"Email notification failed: {e}")

    return {"success": True, "message": "Your message has been received. We will contact you soon."}
