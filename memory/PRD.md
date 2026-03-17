# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" (clone of papermap.ai) with user/admin dashboards, 14-day trial, plan-based restrictions, and AI-powered data analysis.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn/ui, react-joyride, recharts, react-markdown
- **Backend**: FastAPI, Motor (async MongoDB)
- **AI**: GPT-5.2 via emergentintegrations (multi-turn chat)
- **Payments**: Cashfree PG SDK v3 (Production)
- **Database**: MongoDB

## Implemented Features

### User Dashboard (Fully Redesigned)
- [x] **Tab Navigation**: Dashboard | Notes | Reports | Data Sources | AI Visibility
- [x] **Stats Overview**: 4 dynamic cards (Workspaces, Files, AI Queries, Plan) with badges
- [x] **Auto-Generated Charts** (on file upload): KPI cards, Bar, Line, Donut charts, Data Tables
- [x] **AI Search Bar**: Persistent bottom chat bar, ChatGPT-like multi-turn conversation, minimize/expand
- [x] **Notes**: Full CRUD with modal editor
- [x] **Reports**: Lists uploaded files as reports with view/export
- [x] **Data Sources**: Grid of available integrations
- [x] **AI Visibility**: URL analysis for SEO and AI discoverability scores
- [x] **Clickable Workspace Cards** -> WorkspaceView with interactive AI chat

### WorkspaceView
- [x] Interactive multi-turn AI chat (GPT-5.2, session persistence)
- [x] Tabs: AI Chat | Files | Sources
- [x] File upload scoped to workspace, file analytics, integrations

### Admin Dashboard
- [x] 5 tabs: Dashboard, Users, Data Sources, Revenue, Slack

### Authentication & Trial
- [x] JWT + RBAC, 14-day trial, trial badge, expired popup

### Payments
- [x] Cashfree PG SDK v3 (Production mode)
- [x] Plans: Starter (500 INR/mo, 100 credits), Business Pro (800 INR/mo, 1000 credits)
- [x] Order creation, status check, webhook handling

### Other
- [x] Slack integration, Landing page, Contact form, Legal pages, App tour

## Key API Endpoints
- `POST /api/payments/create-order` - Create Cashfree payment order
- `GET /api/payments/order-status/{order_id}` - Check payment status
- `POST /api/ai-visibility/analyze` - Analyze URL for SEO/AI visibility
- `POST /api/ai/chat` - Multi-turn AI chat
- `GET /api/dashboard/summary` - Dashboard stats + activity
- `GET /api/charts/generate/{file_id}` - Auto-generate chart configs
- `POST/GET/PUT/DELETE /api/charts/notes` - Notes CRUD
- `GET /api/charts/reports` - Reports listing

## Credentials
- Admin: admin@papermap.com / admin123
- Test: testuser@test.com / test1234

## Testing Status (Iteration 10 - March 2026)
- Backend: 91% (20/22 passed)
- Frontend: 100% (10/10 features verified)
- All P0 issues resolved

## Backlog

### P1
- [ ] Admin Dashboard "Data Sources" and "Revenue" tabs with real data

### P2
- [ ] Social Logins (Google & Microsoft OAuth)
- [ ] Editable Dashboard Layout (drag-and-drop)
- [ ] Google/Meta Ads frontend wiring

### P3
- [ ] Email Verification on Login (2FA)
- [ ] Admin Slack Integration panel
- [ ] Forgot Password backend (token gen, email sending)
- [ ] Refactor UserDashboard.jsx into smaller components (~1300 lines)
