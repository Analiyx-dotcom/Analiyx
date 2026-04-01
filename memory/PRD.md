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
- **Starter**: 6,000/year, 100 credits/month, 4 data sources, 1 workspace
- **Business Pro**: 9,000/year, 1,000 credits/month, unlimited sources, 10 workspaces

## Implemented Features

### Authentication & User Management
- [x] JWT auth with role-based access (user/admin)
- [x] 7-day free trial for new users (Trial plan, 50 credits)
- [x] Trial expired popup forcing plan selection
- [x] Disabled/spam users strictly blocked (login + existing sessions)
- [x] Subscription duration tracking
- [x] Phone number collected on signup
- [x] Unique Client ID (ANX-XXXXX) generated per registration

### Payments (Razorpay Live)
- [x] Razorpay checkout SDK integration
- [x] Order creation, payment verification, webhook handling
- [x] 1-year subscription per payment
- [x] Coupon code system (admin-created coupons with % discount)
- [x] Coupon validation endpoint for client-side verification
- [x] Coupon applied during Razorpay checkout adjusts amount

### Integrations (OAuth)
- [x] Google Ads - OAuth connect/disconnect with callback
- [x] Google Analytics - OAuth connect/disconnect with callback
- [x] Meta Ads - OAuth connect/disconnect with callback
- [x] Simple Connect buttons on Data Sources tab
- [x] Integration status tracking per user

### Admin Dashboard
- [x] Dashboard overview with stats
- [x] User Management: Activate/Disable/Block as Spam, Extend Trial/Subscription, Manage Credits
- [x] Users table shows Client ID, Phone, Name, Email, Plan, Credits, Status columns
- [x] Search bar to filter users by Client ID, Phone, Name or Email
- [x] Support Tickets: View, reply, close
- [x] Coupon Management: Create, list, toggle active/inactive, delete coupons
- [x] User Export: Excel (.xlsx) and PDF
- [x] Data Sources overview, Revenue breakdown, Slack integration

### User Dashboard
- [x] Tab navigation: Dashboard | Notes | Reports | Data Sources | AI Visibility
- [x] Auto-generated charts, AI Chat Bar, Notes CRUD
- [x] AI Visibility Deep Report (min 1 page, citations, detailed analysis)
- [x] Subscription info display (plan, credits, expiry date, trial end)
- [x] Workspace management with detail views
- [x] Upgrade modal with coupon code input and Apply button

### Google Analytics & SEO
- [x] Google Analytics (gtag.js) tags in index.html
- [x] Google Webmaster site verification meta tag

## Credentials
- Admin: Admin@analiyx.com / 1234
- Test: testuser@test.com / test1234
- Test with phone: phoneuser@test.com / test1234

## Razorpay Keys
- Key ID: rzp_live_STOut8Uckvo5mM
- Secret: axQBMcKBsdh23B2hVn62VHX1

## Key API Endpoints
- `POST /api/payments/create-order` - Razorpay order with optional coupon_code
- `POST /api/payments/verify-payment` - Verify Razorpay signature
- `POST /api/payments/validate-coupon` - Validate coupon and return discount info
- `POST /api/admin/manage/coupons` - Create coupon (admin)
- `GET /api/admin/manage/coupons` - List coupons (admin)
- `PUT /api/admin/manage/coupons/{id}/toggle` - Toggle coupon active/inactive
- `DELETE /api/admin/manage/coupons/{id}` - Delete coupon
- `GET /api/integrations/connect/{service}` - Get OAuth URL
- `PUT /api/admin/manage/users/{id}/status` - Activate/Disable/Spam
- `GET /api/admin/manage/users/export/{format}` - Export users (excel/pdf)
- `POST /api/ai-visibility/analyze` - Deep AI Visibility report

## Known Issues
- Gmail SMTP authentication failing (Google blocking app passwords) - BLOCKED
- Email notifications (welcome, ticket reply, payment receipt) not working due to SMTP
- Free LLM API replacement - NOT STARTED (for self-hosted deployment)

## Backlog

### P2
- [ ] Social Logins (Google & Microsoft OAuth)
- [ ] Editable Dashboard Layout (drag-and-drop)
- [ ] Support ticket email notifications (needs SMTP fix or switch to Resend/SendGrid)

### P3
- [ ] Email Verification on Login (2FA)
- [ ] Forgot Password backend
- [ ] Refactor UserDashboard.jsx (~1400 lines)
