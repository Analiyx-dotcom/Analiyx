# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed clone of https://www.papermap.ai with a separate admin dashboard for analytics, rebranded as "Analiyx".

## Tech Stack
- **Frontend**: React, React Router, Tailwind CSS, Shadcn/ui, react-joyride
- **Backend**: FastAPI, Pydantic, Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: JWT with RBAC
- **Payments**: Cashfree PG SDK v3 (Production)
- **AI**: GPT-5.2 via emergentintegrations

## Implemented Features

### Landing Page
- [x] "Try for Free" hero → /signup, Dashboard preview, Indian testimonials
- [x] Pricing in INR, Footer with techmeliora@gmail.com, Legal links

### Authentication & Trial
- [x] JWT login/signup with RBAC (user/admin)
- [x] 14-day free trial, floating badge, expired popup, admin trial extension

### User Dashboard (REDESIGNED - P2)
- [x] **Welcome Hero** — Date, personalized greeting, gradient background
- [x] **Stats Overview** — 4 dynamic cards (Workspaces, Files, AI Queries, Plan) with "+X this week" badges
- [x] **Quick Actions** — Create Workspace, Upload File, AI Visibility, Browse Integrations
- [x] **2/3 + 1/3 Layout** — Workspaces & files left, Plan card + Activity feed + CTA right
- [x] **Recent Activity Feed** — Color-coded activity items (uploads, workspace creations, AI searches)
- [x] **Clickable Workspace Cards** → WorkspaceView detail with integrations, AI search, file upload
- [x] **WorkspaceView** — Connected sources, AI Search bar (GPT-5.2), file upload/analytics, integrations modal
- [x] AI Visibility analysis, Take a Tour (Joyride), Support tickets, Slack integration
- [x] Cashfree payment (SDK v3), Report download, File deletion

### Admin Dashboard
- [x] 5 tabs: Dashboard, Users, Data Sources, Revenue, Slack
- [x] Stats, user management, charts, Slack connection panel

### Backend API Endpoints
- `/api/dashboard/summary` — Dynamic stats + activity feed
- `/api/ai/search` — GPT-5.2 workspace-scoped AI search
- `/api/data-sources/upload-file?workspace_id` — Workspace-scoped uploads
- `/api/payments/create-order` — Cashfree payment
- `/api/ai/analyze-url` — AI Visibility
- Full CRUD for workspaces, files, users, Slack

## Architecture
```
/app/backend/routes/ — auth, admin, data_source, workspace, ai_search, ai_visibility, dashboard, payment, slack, contact, support, integration
/app/frontend/src/pages/ — UserDashboard, WorkspaceView, AdminDashboard, Login, Signup, Home, Contact, Legal
```

## Credentials
- Admin: admin@papermap.com / admin123
- Test: testpay@analiyx.com / test1234

## Backlog
### P2 - Medium
- [ ] Google Ads & Meta Ads OAuth flow (frontend wiring)

### P3 - Lower
- [ ] Gmail + Microsoft OAuth signup
- [ ] Email verification on login (2FA)
- [ ] Forgot Password backend (email sending)
- [ ] Refactor UserDashboard.jsx into smaller components
