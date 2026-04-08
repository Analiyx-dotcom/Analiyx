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

### Google Ads Integration (via Nango)
- [x] Connect Google Ads button via Nango OAuth
- [x] Backend: GET /api/google-ads/customers (list accessible customer IDs)
- [x] Backend: GET /api/google-ads/campaigns (GAQL query for campaigns with metrics)
- [x] Frontend: GoogleAdsDashboard component with 4 summary cards (Spend, Clicks, Impressions, Conversions)
- [x] Frontend: CampaignsTable showing name, status, type, budget, impressions, clicks, CTR, CPC, cost, conversions
- [x] Not-connected state with clear message and Retry button

### Nango OAuth Integrations
- [x] NangoService utility (connect sessions, save/get/delete connections, proxy)
- [x] 5 API endpoints: connect-session, save-connection, connections, disconnect, proxy
- [x] NangoConnect component: Google Ads, Google Analytics, Google Sheets, Meta Ads

### Authentication & User Management
- [x] JWT auth, RBAC, 7-day trial, phone + Client ID on signup
- [x] Settings page (profile update, change password)

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

## Credentials
- Admin: Admin@analiyx.com / 1234
- Test: testuser@test.com / test1234
- Nango Secret: ae6ff9d5-8289-4a48-baa3-b80e9e1f6c0f

## Known Issues
- Gmail SMTP BLOCKED (Google rejecting app passwords)

## Backlog
### P1
- [ ] Chart color theme selector (6 themes)
- [ ] Bookmark chat messages to Notes
- [ ] Monthly credit reset cron

### P2
- [ ] Social Logins, Editable Dashboard

### P3
- [ ] Email Verification, Forgot Password backend, Refactor UserDashboard.jsx
