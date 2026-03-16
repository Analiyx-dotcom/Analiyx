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
14. Admin dashboard sidebar tabs (Users, Data Sources, Revenue, Slack)
15. All revenue in INR
16. View analytics in graphical format (charts, pie diagrams)
17. AI Visibility feature with LLM
18. Slack integration
19. Cashfree payment gateway integration

## Tech Stack
- **Frontend**: React, React Router, Tailwind CSS, Shadcn/ui, react-joyride
- **Backend**: FastAPI, Pydantic, Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: JWT with RBAC
- **Payments**: Cashfree PG SDK (Production)
- **AI**: GPT-5.2 via emergentintegrations
- **Scraping**: httpx + BeautifulSoup4

## Implemented Features

### Landing Page
- [x] "Try for Free" hero button -> /signup
- [x] Dashboard preview with stats cards and charts
- [x] Indian testimonials (Priya Sharma, Rajesh Menon, Ananya Reddy)
- [x] "Talk to Us" nav link -> /contact
- [x] Pricing in INR
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
- [x] Workspace deletion with confirmation
- [x] File upload (CSV/Excel) with analytics
- [x] Graphical file analytics (bar charts, data type distribution, numeric stats)
- [x] AI Visibility analysis (GPT-5.2 powered URL analysis with scores)
- [x] AI Search Bar (natural language queries over user data, GPT-5.2)
- [x] Take a Tour (react-joyride guided tour for new users)
- [x] Support ticket creation (subject, priority, message)
- [x] Browse integrations modal (Practo API, Notion API, Zoho CRM, Google Analytics, etc.)
- [x] Report download (PDF/Excel)
- [x] Upgrade modal with Cashfree payment (SDK v3)
- [x] Slack integration panel

### Admin Dashboard
- [x] 5 working sidebar tabs (Dashboard, Users, Data Sources, Revenue, Slack)
- [x] Stats cards with growth indicators
- [x] User management table (Enable/Disable, +7 Days, + Credits)
- [x] User Growth chart
- [x] Revenue Trend chart (INR)
- [x] Revenue by Plan breakdown
- [x] Data Sources overview with per-user breakdown
- [x] Slack Integration panel (connect/disconnect)

### Pages
- [x] Contact form (/contact)
- [x] Legal page (/legal) - Privacy, Terms, Cookies
- [x] Login, Signup, Forgot Password

### Integrations
- [x] Cashfree Payment Gateway (Production keys, SDK v3)
- [x] GPT-5.2 via emergentintegrations (AI Visibility + AI Search)
- [x] CSV/Excel file upload and analysis
- [x] Slack integration (user + admin)

## Architecture
```
/app/backend/
  server.py, auth.py, models.py, seed_database.py
  routes/
    auth_routes.py, admin_routes.py, admin_management_routes.py
    data_source_routes.py, integration_routes.py
    contact_routes.py, support_routes.py, workspace_routes.py
    ai_visibility_routes.py, ai_search_routes.py
    payment_routes.py, slack_routes.py

/app/frontend/src/
  App.js, pages/ (Login, Signup, UserDashboard, AdminDashboard, ContactPage, LegalPage, ForgotPassword)
  components/ (Hero, Navbar, Footer, Pricing, Testimonials, Integrations, ui/)
  services/api.js, mock/mockData.js, utils/reportExport.js
```

## Credentials
- Admin: admin@papermap.com / admin123
- Test User: testpay@analiyx.com / test1234
- Cashfree: APP_ID=42270719d5a1418ed37be96ed5707224 (Production)

## Backlog
### P2 - Medium Priority
- [ ] Impressive User Dashboard redesign (better charts, visual appeal)
- [ ] Google Ads & Meta Ads OAuth flow (frontend wiring)

### P3 - Lower Priority
- [ ] Gmail + Microsoft OAuth signup (item 10)
- [ ] Email verification code on login (item 11)
- [ ] Forgot Password backend (email sending)
- [ ] Real-time data from connected integrations on dashboard
- [ ] Refactor UserDashboard.jsx into smaller components
