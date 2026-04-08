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

### Post-Signup Onboarding Chat (April 8, 2026) — NEW
- [x] Interactive Papermap-style chat flow at /onboarding
- [x] 9 questions: Usage type, Company name, Location, Description, Industry, Monthly MRR, Data Analyst, Digital Marketing, Data Preference
- [x] Chip-based and free-text inputs with typing animation
- [x] Personal flow skips company questions
- [x] "Connect Data" → Data Sources tab, "Sample Data" → Dashboard
- [x] Data saved to user profile (onboarding_data field)
- [x] Admin Dashboard shows Company & Industry columns
- [x] Login/signup redirects non-onboarded users to /onboarding
- [x] Completed users skip onboarding automatically

### Credit System
- [x] AI Chat: 1 credit, AI Visibility: 5 credits, File Upload: 2 credits
- [x] Insufficient credits check, usage logging

### Payments & Coupons
- [x] Razorpay checkout, coupon codes, validation

### Admin Dashboard
- [x] User management, search, coupon CRUD, tickets, exports
- [x] Onboarding data visible in user table (Company, Industry columns)

### AI Features
- [x] AI Visibility Deep Report with citations
- [x] AI Chat (GPT-5.2, token-optimized)

### Nango OAuth Integrations
- [x] NangoService utility with connection_config.scopes
- [x] NangoConnect component: Google Ads, GA, Sheets, Meta Ads

### Google Ads Integration (via Nango) — FIXED April 8, 2026
- [x] Base-Url-Override + nango-proxy-developer-token headers
- [x] API v20, customer account dropdown
- [x] Note: DEVELOPER_TOKEN_NOT_APPROVED blocks production data

### Google Analytics Integration (via Nango) — FIXED April 8, 2026
- [x] analytics.readonly scope via connection_config.scopes
- [x] 403 scope error handling with reconnect guidance

### Chart Color Theme Selector (April 8, 2026)
- [x] 6 themes applied to Recharts (Default, Forest, Azure, Mint, Violet, Ocean)

### Bookmark AI Chat to Notes (April 8, 2026)
- [x] Hover bookmark on assistant messages, saves to Notes

## Credentials
- Admin: Admin@analiyx.com / 1234
- Test: testuser@test.com / test1234
- Nango Secret: ae6ff9d5-8289-4a48-baa3-b80e9e1f6c0f

## Known Issues
- Gmail SMTP BLOCKED (Google rejecting app passwords)
- Google Ads: DEVELOPER_TOKEN_NOT_APPROVED (needs Google approval)

## Backlog
### P1
- [ ] Monthly credit reset cron (reset credits at billing cycle start)

### P2
- [ ] Social Logins (Google & Microsoft OAuth)

### P3
- [ ] Editable Dashboard Layout (drag-and-drop)
- [ ] Email Verification (2FA)
- [ ] Forgot Password Backend
- [ ] Refactor UserDashboard.jsx (~1500 lines)
