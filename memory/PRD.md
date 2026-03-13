# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed clone of https://www.papermap.ai with a separate admin dashboard for analytics, rebranded as "Analiyx".

## Core Requirements (19 Items from User)
1. Get Started / Try for Free button on landing page
2. Dashboard preview on homepage
3. Indian testimonials
4. Contact form page (sends to techmeliora@gmail.com)
5. Legal information page
6. Footer email display
7. Floating trial days remaining badge
8. Trial expired popup with upgrade button
9. Admin trial extension shows updated period
10. Gmail + Microsoft signup (PENDING)
11. Email verification code on login (PENDING)
12. Support ticket / contact system
13. Workspace creation with data sources
14. Admin dashboard sidebar tabs (Users, Data Sources, Revenue)
15. All revenue in INR
16. View analytics in graphical format (charts, pie diagrams)
17. AI Visibility feature with LLM
18. Slack integration (PENDING)
19. Cashfree payment gateway integration

## Tech Stack
- **Frontend**: React, React Router, Tailwind CSS, Shadcn/ui
- **Backend**: FastAPI, Pydantic, Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: JWT with RBAC
- **Payments**: Cashfree PG SDK (Production)
- **AI**: GPT-5.2 via emergentintegrations
- **Scraping**: httpx + BeautifulSoup4

## Implemented Features

### Landing Page
- [x] "Try for Free" hero button → /signup
- [x] Dashboard preview with stats cards and charts
- [x] Indian testimonials (Priya Sharma, Rajesh Menon, Ananya Reddy)
- [x] "Talk to Us" nav link → /contact
- [x] Pricing in INR (₹2,999 / ₹7,999 / Custom)
- [x] Footer with techmeliora@gmail.com email
- [x] Legal links (Privacy, Terms, Cookies)

### Authentication & Trial
- [x] JWT-based login/signup with role-based redirects
- [x] 14-day free trial on signup
- [x] Floating trial badge (bottom-left, shows days remaining)
- [x] Trial expired popup with Upgrade button
- [x] Admin can extend trials (+7 days)
- [x] Forgot password page

### User Dashboard
- [x] User info cards (Plan, Credits, Status)
- [x] Workspace creation modal (name + data source selection)
- [x] Workspace display with data source tags
- [x] File upload (CSV/Excel) with analytics
- [x] Graphical file analytics (bar charts, data type distribution, numeric stats)
- [x] AI Visibility analysis (GPT-5.2 powered URL analysis with scores)
- [x] Support ticket creation (subject, priority, message)
- [x] Browse integrations modal
- [x] Report download (PDF/Excel)
- [x] Upgrade modal with Cashfree payment

### Admin Dashboard
- [x] 4 working sidebar tabs (Dashboard, Users, Data Sources, Revenue)
- [x] Stats cards with growth indicators
- [x] User management table (Enable/Disable, +7 Days, + Credits)
- [x] User Growth chart
- [x] Revenue Trend chart (INR)
- [x] Revenue by Plan breakdown
- [x] Data Sources overview

### Pages
- [x] Contact form (/contact) → saves to DB + email notification
- [x] Legal page (/legal) → Privacy, Terms, Cookies
- [x] Login, Signup, Forgot Password

### Integrations
- [x] Cashfree Payment Gateway (Production keys)
- [x] GPT-5.2 via emergentintegrations (AI Visibility)
- [x] CSV/Excel file upload and analysis

## Architecture
```
/app/backend/
  server.py, auth.py, models.py, seed_database.py
  routes/
    auth_routes.py, admin_routes.py, admin_management_routes.py
    data_source_routes.py, integration_routes.py
    contact_routes.py, support_routes.py, workspace_routes.py
    ai_visibility_routes.py, payment_routes.py

/app/frontend/src/
  App.js, pages/ (Login, Signup, UserDashboard, AdminDashboard, ContactPage, LegalPage, ForgotPassword)
  components/ (Hero, Navbar, Footer, Pricing, Testimonials, ui/)
  services/api.js, mock/mockData.js, utils/reportExport.js
```

## Credentials
- Admin: admin@papermap.com / admin123
- Test User: testuser@analiyx.com / test1234
- Cashfree: APP_ID=42270719d5a1418ed37be96ed5707224 (Production)

## Backlog
### P1 - High Priority
- [ ] Gmail + Microsoft OAuth signup (item 10)
- [ ] Email verification code on login (item 11)

### P2 - Medium Priority
- [ ] Slack integration for report sharing (item 18) — DONE
- [ ] Google Ads & Meta Ads OAuth flow
- [ ] Zoho Books & Google Sheets integrations
- [ ] Welcome email on signup

### P3 - Lower Priority
- [ ] Forgot Password backend (email sending)
- [ ] Real-time data from connected integrations on dashboard
- [ ] Refactor UserDashboard.jsx into smaller components
