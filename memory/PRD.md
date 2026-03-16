# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" with user/admin dashboards, 14-day trial, plan-based restrictions, and AI-powered data analysis.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn/ui, react-joyride
- **Backend**: FastAPI, Motor (async MongoDB)
- **AI**: GPT-5.2 via emergentintegrations (multi-turn chat)
- **Payments**: Cashfree PG SDK v3

## Implemented Features

### User Dashboard (P2 Redesigned)
- [x] Welcome Hero with stats overview (Workspaces, Files, AI Queries, Plan)
- [x] Quick Actions grid + 2/3+1/3 layout + Recent Activity feed
- [x] Clickable workspace cards → WorkspaceView

### WorkspaceView — Interactive AI Chat (NEW)
- [x] **ChatGPT-like multi-turn AI chat** scoped to workspace data
- [x] Chat history persistence (session_id per workspace)
- [x] Chat history loads on workspace open
- [x] Markdown rendering (bold, headers, bullets, tables)
- [x] Typing indicator (bouncing dots) while AI processes
- [x] Quick prompts in empty state ("Summarize my data", etc.)
- [x] User messages (purple, right) / AI messages (dark, left)
- [x] Tab navigation: AI Chat | Files | Sources
- [x] File upload scoped to workspace
- [x] File analytics modal
- [x] Integration connection modal

### Admin Dashboard
- [x] 5 tabs: Dashboard, Users, Data Sources, Revenue, Slack

### Authentication & Trial
- [x] JWT + RBAC, 14-day trial, trial badge, expired popup

### Other
- [x] Cashfree payment (SDK v3), AI Visibility, Slack integration
- [x] Landing page, contact form, legal pages, Take a Tour

## API Endpoints
- `POST /api/ai/chat` — Multi-turn AI chat with session persistence
- `GET /api/ai/chat/history/{workspace_id}` — Load chat history
- `POST /api/ai/search` — Legacy single-query (backward compatible)
- `GET /api/dashboard/summary` — Dashboard stats + activity feed
- `POST /api/data-sources/upload-file?workspace_id` — Workspace-scoped upload
- Full CRUD for workspaces, files, users, payments, Slack

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
