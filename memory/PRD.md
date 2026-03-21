# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" (clone of papermap.ai) with user/admin dashboards, 14-day free trial system, plan-based restrictions, and AI-powered data analysis.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn/ui, Recharts, react-markdown, react-joyride
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic
- **AI**: GPT-5.2 via emergentintegrations (Emergent LLM Key)
- **Payments**: Razorpay (Live keys)
- **Database**: MongoDB

## Implemented Features

### Authentication & User Management
- [x] JWT auth with role-based access (user/admin)
- [x] 7-day free trial for new users (Trial plan, 50 credits)
- [x] Trial expired popup forcing plan selection
- [x] Disabled/spam users strictly blocked from login (403)
- [x] Subscription duration tracking (subscription_end_date field)

### Payments (Razorpay)
- [x] Razorpay checkout SDK integration (replaced Cashfree)
- [x] Plans: Starter (₹500/mo, 100 credits), Business Pro (₹800/mo, 1000 credits)
- [x] Order creation, payment verification, webhook handling
- [x] 1-year subscription duration per payment

### Admin Dashboard
- [x] Dashboard overview with stats (Users, Subscriptions, Revenue, Data Sources)
- [x] User Management: Activate/Disable/Block as Spam, Extend Trial (+7d), Extend Subscription (+1Y/+2Y), Manage Credits (+Cr)
- [x] Support Tickets: View all tickets, reply, close
- [x] User Export: Download users as Excel (.xlsx) or PDF
- [x] Data Sources: Overview of connected sources across users
- [x] Revenue: Revenue breakdown and trends
- [x] Slack Integration: Connect workspace for admin notifications

### User Dashboard
- [x] Tab navigation: Dashboard | Notes | Reports | Data Sources | AI Visibility
- [x] Auto-generated charts from uploaded data (KPI, Bar, Line, Donut)
- [x] AI Chat Bar (persistent bottom bar, minimize/expand, multi-turn GPT-5.2)
- [x] Notes CRUD with modal editor
- [x] Reports listing
- [x] AI Visibility URL analysis (SEO/AI scores)
- [x] Subscription info display (plan, credits, expiry date, trial end)
- [x] Workspace management with detail views

### Workspace Detail View
- [x] Interactive multi-turn AI chat (GPT-5.2, session persistence)
- [x] File upload scoped to workspace
- [x] Connected data sources

## Key API Endpoints
- `POST /api/auth/register` - Register (creates Trial plan, 7-day trial)
- `POST /api/auth/login` - Login (blocks disabled/spam users)
- `POST /api/payments/create-order` - Create Razorpay order
- `POST /api/payments/verify-payment` - Verify Razorpay signature
- `PUT /api/admin/manage/users/{id}/status` - Activate/Disable/Spam
- `PUT /api/admin/manage/users/{id}/subscription` - Extend subscription
- `POST /api/admin/manage/users/{id}/extend-trial` - Extend trial
- `GET /api/admin/manage/tickets` - Admin view all tickets
- `POST /api/admin/manage/tickets/{id}/reply` - Admin reply to ticket
- `GET /api/admin/manage/users/export/excel` - Export users xlsx
- `GET /api/admin/manage/users/export/pdf` - Export users pdf
- `POST /api/ai-visibility/analyze` - AI URL analysis
- `POST /api/ai/chat` - Multi-turn AI chat

## Credentials
- Admin: admin@papermap.com / admin123
- Test: testuser@test.com / test1234

## Razorpay Keys
- Key ID: rzp_live_STOut8Uckvo5mM
- Secret: axQBMcKBsdh23B2hVn62VHX1

## Testing Status (Iteration 11 - March 2026)
- Backend: 100% (14/14 passed)
- Frontend: 100% (16/16 features verified)

## Backlog

### P2
- [ ] Social Logins (Google & Microsoft OAuth)
- [ ] Editable Dashboard Layout (drag-and-drop charts)
- [ ] Google/Meta Ads frontend wiring
- [ ] Support ticket email notifications

### P3
- [ ] Email Verification on Login (2FA)
- [ ] Admin Slack Integration panel enhancements
- [ ] Forgot Password backend (token gen, email sending)
- [ ] Refactor UserDashboard.jsx into smaller components (~1400 lines)
