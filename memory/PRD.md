# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" (clone of papermap.ai) with user/admin dashboards, trial system, plan-based restrictions, and AI-powered data analysis.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn/ui, Recharts, @nangohq/frontend
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic, Nango SDK
- **AI**: GPT-5.2 via emergentintegrations (Emergent LLM Key)
- **Payments**: Razorpay (Live keys)
- **OAuth**: Nango (managed OAuth)
- **Database**: MongoDB

## Pricing Plans
- **Trial**: Free 7 days, 100 credits (one-time)
- **Starter**: ₹9,999/year, 200 credits/month
- **Business Pro**: ₹14,999/year, 500 credits/month

## Implemented Features

### Authentication & User Management
- [x] JWT auth, RBAC, 7-day trial, phone + Client ID on signup
- [x] Settings page (/settings) for profile update and password change

### Credit System
- [x] AI Chat: 1 credit, AI Visibility: 5 credits, File Upload: 2 credits
- [x] Insufficient credits check, usage logging

### Payments & Coupons
- [x] Razorpay checkout, coupon codes, validation

### Admin Dashboard
- [x] User management, search, coupon CRUD, tickets, exports

### AI Features
- [x] AI Visibility Deep Report with citations
- [x] AI Chat (GPT-5.2, token-optimized)

### Nango OAuth Integrations
- [x] NangoService utility (connect sessions, save/get/delete connections, proxy)
- [x] 5 API endpoints: connect-session, save-connection, connections, disconnect, proxy
- [x] NangoConnect component: Google Ads, Google Analytics, Google Sheets, Meta Ads

### Google Ads Integration (via Nango)
- [x] Connect Google Ads button via Nango OAuth
- [x] Backend: GET /api/google-ads/customers, GET /api/google-ads/campaigns
- [x] Frontend: GoogleAdsDashboard with summary cards and campaigns table

### Google Analytics Integration (via Nango)
- [x] GA4 Nango scope fix: connection_config.scopes with analytics.readonly (April 8, 2026)
- [x] Backend: GET /api/google-analytics/properties, /report, POST /set-property
- [x] Frontend: GoogleAnalyticsDashboard with charts, tables, traffic sources
- [x] Enhanced error handling for 403 scope errors with reconnect guidance

### Chart Color Theme Selector (April 8, 2026)
- [x] 6 themes: Default, Forest, Azure, Mint, Violet, Ocean
- [x] Backend: PUT /api/charts/theme, GET /api/charts/theme
- [x] Frontend: ChartThemeSelector component with dropdown
- [x] Theme colors applied to AnalyticsDashboard charts (bar, line, donut)
- [x] Theme persisted per user in MongoDB

### Bookmark AI Chat to Notes (April 8, 2026)
- [x] Bookmark icon on assistant chat messages (hover to reveal)
- [x] Saves message content as a Note via POST /api/charts/notes
- [x] Toast confirmation on bookmark
- [x] Notes accessible in Notes tab

## Credentials
- Admin: Admin@analiyx.com / 1234
- Test: testuser@test.com / test1234
- Nango Secret: ae6ff9d5-8289-4a48-baa3-b80e9e1f6c0f

## Known Issues
- Gmail SMTP BLOCKED (Google rejecting app passwords)
- GA4 data fetch requires user to disconnect and reconnect after scope fix

## Backlog
### P1
- [ ] Monthly credit reset cron (reset credits at billing cycle start based on active plan)

### P2
- [ ] Social Logins (Google & Microsoft OAuth for app registration/login)

### P3
- [ ] Editable Dashboard Layout (drag-and-drop)
- [ ] Email Verification (2FA)
- [ ] Forgot Password Backend
- [ ] Refactor UserDashboard.jsx (currently ~1500 lines)
