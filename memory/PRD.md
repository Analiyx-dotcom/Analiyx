# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" (clone of papermap.ai) with user/admin dashboards, trial system, plan-based restrictions, and AI-powered data analysis. The user hired an external developer to handle actual API/Nango integrations. The AI engineer focuses on making the web application visually and graphically ready with sample fallback data.

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

### Post-Signup Onboarding Chat (April 8, 2026)
- [x] Interactive Papermap-style chat flow at /onboarding
- [x] 9 questions with chip-based and free-text inputs
- [x] Data saved to user profile (onboarding_data field)
- [x] Admin Dashboard shows Company & Industry columns

### Credit System
- [x] AI Chat: 1 credit, AI Visibility: 5 credits, File Upload: 2 credits
- [x] Insufficient credits check, usage logging

### Payments & Coupons
- [x] Razorpay checkout, coupon codes, validation

### Admin Dashboard
- [x] User management, search, coupon CRUD, tickets, exports
- [x] Onboarding data visible in user table

### AI Features
- [x] AI Visibility Deep Report with citations
- [x] AI Chat (GPT-5.2, token-optimized)

### Nango OAuth Integrations
- [x] NangoService utility with connection_config.scopes
- [x] NangoConnect component: Google Ads, GA, Sheets, Meta Ads

### Dashboard Integrations (Sample Data — April 16, 2026)
- [x] Google Analytics Dashboard — Sessions, Users, Page Views, Bounce Rate, Traffic Sources
- [x] Google Ads Dashboard — Campaigns, Impressions, Clicks, CTR, Cost, Conversions
- [x] Meta Ads Dashboard — Campaigns, Reach, Spend, Age Demographics, Platform Breakdown
- [x] Google Sheets Dashboard — Sheet preview, chart visualization, multi-sheet tabs
- [x] **Shopify Dashboard (NEW)** — Orders, Revenue, Visitors, Conversion Rate, Top Products, Recent Orders, Traffic Sources
- [x] **Zoho Dashboard (NEW)** — Books (Income/Expenses, Invoices, Profit Trend) + CRM (Pipeline, Deals, Lead Sources) with tab toggle

### API Documentation (April 16, 2026)
- [x] **API_CONTRACTS.md** — Complete JSON response schemas for all 7 dashboard endpoints for the hired external developer

### Chart Color Theme Selector
- [x] 6 themes applied to Recharts (Default, Forest, Azure, Mint, Violet, Ocean)

### Bookmark AI Chat to Notes
- [x] Hover bookmark on assistant messages, saves to Notes

### VPS Deployment
- [x] PM2 ecosystem, Nginx proxy, Hostinger KVM VPS compatible via relative API paths

## Credentials
- Admin: Admin@analiyx.com / 1234
- Test: testuser@test.com / test1234
- Nango Secret: ae6ff9d5-8289-4a48-baa3-b80e9e1f6c0f

## Known Issues
- Gmail SMTP BLOCKED (Google rejecting app passwords)
- Google Ads: DEVELOPER_TOKEN_NOT_APPROVED (needs Google approval)
- Nango: Free tier connection limits (external constraint)

## Backlog
### P1
- [ ] Monthly credit reset cron (reset credits at billing cycle start)
- [ ] UI/UX polish alignment with papermap.ai aesthetic

### P2
- [ ] Social Logins (Google & Microsoft OAuth)

### P3
- [ ] Editable Dashboard Layout (drag-and-drop)
- [ ] Email Verification (2FA)
- [ ] Forgot Password Backend
- [ ] Refactor UserDashboard.jsx (~1500 lines → extract into smaller components)
