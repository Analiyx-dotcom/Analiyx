# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" with user/admin dashboards, 14-day trial, plan-based restrictions, and AI-powered data analysis.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn/ui, react-joyride, recharts
- **Backend**: FastAPI, Motor (async MongoDB)
- **AI**: GPT-5.2 via emergentintegrations (multi-turn chat)
- **Payments**: Cashfree PG SDK v3

## Implemented Features

### User Dashboard (Fully Redesigned)
- [x] **Tab Navigation**: Dashboard | Notes | Reports | Data Sources
- [x] **Stats Overview**: 4 dynamic cards (Workspaces, Files, AI Queries, Plan) with badges
- [x] **Auto-Generated Charts** (on file upload):
  - KPI Metric Cards (rows, cols, type, averages, totals)
  - Bar Chart (column comparisons)
  - Line Chart (growth/trends)
  - Donut Charts (data type & category distribution)
  - Data Tables (sample data, numeric statistics)
  - Chart actions: Expand/fullscreen, Delete
- [x] **AI Search Bar** — Persistent at bottom of dashboard, ChatGPT-like multi-turn conversation
- [x] **Notes** — Full CRUD (Create, Read, Update, Delete) with modal editor
- [x] **Reports** — Lists all uploaded files as reports with view/export
- [x] **Data Sources** — Grid of all available integrations
- [x] **Clickable Workspace Cards** → WorkspaceView with interactive AI chat

### WorkspaceView
- [x] Interactive multi-turn AI chat (GPT-5.2, session persistence)
- [x] Tabs: AI Chat | Files | Sources
- [x] File upload scoped to workspace, file analytics, integrations

### Admin Dashboard
- [x] 5 tabs: Dashboard, Users, Data Sources, Revenue, Slack

### Authentication & Trial
- [x] JWT + RBAC, 14-day trial, trial badge, expired popup

### Other
- [x] Cashfree payment (SDK v3), AI Visibility, Slack integration
- [x] Landing page, contact form, legal pages, Take a Tour

## Key API Endpoints
- `GET /api/charts/generate/{file_id}` — Auto-generate chart configs
- `POST/GET/PUT/DELETE /api/charts/notes` — Notes CRUD
- `GET /api/charts/reports` — Reports listing
- `POST /api/ai/chat` — Multi-turn AI chat
- `GET /api/dashboard/summary` — Dashboard stats + activity

## Credentials
- Admin: admin@papermap.com / admin123
- Test: testpay@analiyx.com / test1234

## Backlog
### P2
- [ ] Google Ads & Meta Ads OAuth frontend wiring
### P3
- [ ] Gmail + Microsoft OAuth signup
- [ ] Email verification on login (2FA)
- [ ] Forgot Password backend (email sending)
- [ ] Refactor UserDashboard.jsx into smaller components
