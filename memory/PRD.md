# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" (clone of papermap.ai) with user/admin dashboards, trial system, plan-based restrictions, and AI-powered data analysis.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn/ui, Recharts, react-markdown, react-joyride
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic
- **AI**: GPT-5.2 via emergentintegrations (Emergent LLM Key)
- **Payments**: Razorpay (Live keys)
- **Database**: MongoDB

## Pricing Plans
- **Trial**: Free 7 days, 50 credits, all features
- **Starter**: ₹6,000/year, 100 credits/month, 4 data sources, 1 workspace
- **Business Pro**: ₹9,000/year, 1,000 credits/month, unlimited sources, 10 workspaces

## Implemented Features

### Authentication & User Management
- [x] JWT auth with role-based access (user/admin)
- [x] 7-day free trial for new users (Trial plan, 50 credits)
- [x] Trial expired popup forcing plan selection
- [x] Disabled/spam users strictly blocked (login + existing sessions)
- [x] Subscription duration tracking

### Payments (Razorpay Live)
- [x] Razorpay checkout SDK integration
- [x] Order creation, payment verification, webhook handling
- [x] 1-year subscription per payment

### Integrations (OAuth)
- [x] Google Ads - OAuth connect/disconnect with callback
- [x] Google Analytics - OAuth connect/disconnect with callback
- [x] Meta Ads - OAuth connect/disconnect with callback
- [x] Simple Connect buttons on Data Sources tab
- [x] Integration status tracking per user

### Admin Dashboard
- [x] Dashboard overview with stats
- [x] User Management: Activate/Disable/Block as Spam, Extend Trial/Subscription, Manage Credits
- [x] Support Tickets: View, reply, close
- [x] User Export: Excel (.xlsx) and PDF
- [x] Data Sources overview, Revenue breakdown, Slack integration

### User Dashboard
- [x] Tab navigation: Dashboard | Notes | Reports | Data Sources | AI Visibility
- [x] Auto-generated charts, AI Chat Bar, Notes CRUD, AI Visibility URL analysis
- [x] Subscription info display (plan, credits, expiry date, trial end)
- [x] Workspace management with detail views

## Credentials
- Admin: Admin@analiyx.com / 1234
- Test: testuser@test.com / test1234

## Razorpay Keys
- Key ID: rzp_live_STOut8Uckvo5mM
- Secret: axQBMcKBsdh23B2hVn62VHX1

## Key API Endpoints
- `POST /api/payments/create-order` - Razorpay order (₹6000 Starter, ₹9000 Business Pro)
- `POST /api/payments/verify-payment` - Verify Razorpay signature
- `GET /api/integrations/connect/{service}` - Get OAuth URL (google_ads, google_analytics, meta_ads)
- `GET /api/integrations/status` - User's integration statuses
- `DELETE /api/integrations/disconnect/{service}` - Disconnect integration
- `PUT /api/admin/manage/users/{id}/status` - Activate/Disable/Spam
- `GET /api/admin/manage/users/export/{format}` - Export users (excel/pdf)

## Backlog

### P2
- [ ] Social Logins (Google & Microsoft OAuth)
- [ ] Editable Dashboard Layout (drag-and-drop)
- [ ] Support ticket email notifications

### P3
- [ ] Email Verification on Login (2FA)
- [ ] Forgot Password backend
- [ ] Refactor UserDashboard.jsx (~1400 lines)
