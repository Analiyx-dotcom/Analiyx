# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" (clone of papermap.ai) with user/admin dashboards, trial system, plan-based restrictions, and AI-powered data analysis.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn/ui, Recharts, react-markdown, react-joyride, @nangohq/frontend
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic, Nango SDK
- **AI**: GPT-5.2 via emergentintegrations (Emergent LLM Key)
- **Payments**: Razorpay (Live keys)
- **OAuth**: Nango (managed OAuth)
- **Database**: MongoDB

## Pricing Plans
- **Trial**: Free 7 days, 100 credits (one-time)
- **Starter**: ₹9,999/year, 200 credits/month, 4 data sources, 1 workspace
- **Business Pro**: ₹14,999/year, 500 credits/month, unlimited sources, 10 workspaces

## Credit Costs
- AI Chat: 1 credit/query
- AI Visibility: 5 credits/analysis
- File Upload: 2 credits/file

## Implemented Features

### Authentication & User Management
- [x] JWT auth with role-based access (user/admin)
- [x] 7-day free trial for new users (Trial plan, 100 credits)
- [x] Trial expired popup forcing plan selection
- [x] Disabled/spam users strictly blocked (login + existing sessions)
- [x] Subscription duration tracking
- [x] Phone number collected on signup
- [x] Unique Client ID (ANX-XXXXX) generated per registration
- [x] Settings page (profile update: name, phone; change password)

### Payments (Razorpay Live)
- [x] Razorpay checkout SDK integration
- [x] Order creation, payment verification, webhook handling
- [x] 1-year subscription per payment
- [x] Coupon code system (admin-created coupons with % discount)
- [x] Coupon validation endpoint for client-side verification

### Credit System
- [x] Credits deducted per action (AI Chat=1, AI Visibility=5, File Upload=2)
- [x] Insufficient credits check blocks action with clear error
- [x] Credit usage logging in `credit_usage` collection
- [x] Credits set on plan purchase (not accumulated)

### Nango OAuth Integrations
- [x] NangoService utility (create_connect_session, save/get/delete connections, proxy_get/post)
- [x] Nango routes: POST /connect-session, POST /save-connection, GET /connections, DELETE /connections/{id}, POST /proxy
- [x] NangoConnect frontend component with 4 integrations: Google Ads, Google Analytics, Google Sheets, Meta Ads
- [x] Connect/Disconnect UI with status badges and connection dates

### Admin Dashboard
- [x] Dashboard overview with stats
- [x] User Management: Activate/Disable/Block, Extend Trial/Sub, Manage Credits
- [x] Users table shows Client ID, Phone, Name, Email, Plan, Credits, Status
- [x] Search bar to filter users by Client ID, Phone, Name or Email
- [x] Support Tickets: View, reply, close
- [x] Coupon Management: Create, list, toggle active/inactive, delete
- [x] User Export: Excel (.xlsx) and PDF

### User Dashboard
- [x] Tab navigation: Dashboard | Notes | Reports | Data Sources | AI Visibility
- [x] Auto-generated charts, AI Chat Bar, Notes CRUD
- [x] AI Visibility Deep Report (detailed analysis + citations)
- [x] Subscription info display
- [x] Workspace management

### Google Analytics & SEO
- [x] Google Analytics (gtag.js) tags in index.html
- [x] Google Webmaster site verification meta tag

## Credentials
- Admin: Admin@analiyx.com / 1234
- Test: testuser@test.com / test1234
- Test with phone: phoneuser@test.com / test1234

## Known Issues
- Gmail SMTP authentication failing (Google blocking app passwords) - BLOCKED
- Email notifications not working due to SMTP

## Backlog

### P1
- [ ] Chart color theme selector (6 themes: Default, Forest, Azure, Mint, Violet, Ocean)
- [ ] Bookmark chat messages to Notes section
- [ ] Monthly credit reset cron job for paid plans

### P2
- [ ] Social Logins (Google & Microsoft OAuth)
- [ ] Editable Dashboard Layout (drag-and-drop)

### P3
- [ ] Email Verification on Login (2FA)
- [ ] Forgot Password backend
- [ ] Refactor UserDashboard.jsx (~1400 lines)
