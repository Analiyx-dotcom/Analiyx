# Analiyx — Turn Data Into Decisions

Analytics platform with AI-powered insights, OAuth integrations, and subscription management.

## Tech Stack

- **Frontend**: React 18, Tailwind CSS, Shadcn/ui, Recharts
- **Backend**: FastAPI (Python 3.10+), Motor (async MongoDB)
- **Database**: MongoDB 6.0+
- **AI**: GPT-5.2 via Emergent LLM Key
- **Payments**: Razorpay
- **OAuth**: Nango (Google Ads, GA4, Sheets, Meta Ads)

## System Dependencies

- Node.js 18+ & Yarn
- Python 3.10+ & pip
- MongoDB 6.0+
- Nginx (for production)
- PM2 (for production process management)
- Certbot (for SSL certificates)

## Quick Start (Development)

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your values
python3 server.py

# Frontend (new terminal)
cd frontend
yarn install
cp .env.example .env  # Edit if needed
yarn start
```

## Production Deployment

See **[DEPLOY.md](./DEPLOY.md)** for complete VPS deployment instructions (Hostinger KVM1).

## Project Structure

```
analiyx/
├── backend/
│   ├── routes/          # API route modules
│   ├── server.py        # FastAPI app entry point
│   ├── auth.py          # JWT authentication
│   ├── models.py        # Pydantic models
│   ├── credits.py       # Credit deduction engine
│   ├── nango_service.py # Nango OAuth proxy
│   ├── requirements.txt
│   ├── .env.example
│   └── .env             # (not committed)
├── frontend/
│   ├── src/
│   │   ├── pages/       # Login, Signup, Dashboard, Onboarding, Settings
│   │   ├── components/  # Reusable UI components
│   │   ├── services/    # API client (axios)
│   │   └── constants/   # Chart themes, etc.
│   ├── public/
│   ├── .env.example
│   └── .env             # (not committed)
├── nginx.conf           # Production nginx config
├── ecosystem.config.js  # PM2 config
├── deploy.sh            # Auto-deploy script
├── DEPLOY.md            # Full deployment guide
└── README.md
```
