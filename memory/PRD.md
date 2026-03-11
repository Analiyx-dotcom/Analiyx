# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed clone of https://www.papermap.ai with a separate admin dashboard for analytics, rebranded as "Analiyx".

## Core Requirements
- **Rebranding**: Application name "Analiyx"
- **Localization**: Indian testimonials, INR pricing (3 plans)
- **User Roles**: Admin and regular user with distinct dashboards
- **Authentication**: Email/password + Google Sign-In + Forgot Password
- **Integrations**: CSV/Excel upload, Google Ads, Meta Ads, Zoho Books, Google Sheets
- **AI Visibility**: URL analysis feature using LLM
- **Admin Controls**: User management (enable/disable, trial extension, credits)
- **Reports**: Downloadable dashboard reports (PDF/Excel)
- **Payments**: Cashfree/Razorpay integration

## Tech Stack
- **Frontend**: React, React Router, Tailwind CSS, Shadcn/ui
- **Backend**: FastAPI, Pydantic, Motor (async MongoDB)
- **Database**: MongoDB
- **Auth**: JWT with RBAC

## What's Been Implemented

### Completed (Feb 2026)
- [x] Full-stack app: React frontend + FastAPI backend + MongoDB
- [x] Dark-themed landing page with Analiyx branding
- [x] JWT-based authentication with admin/user roles
- [x] User signup/login with role-based redirects
- [x] Admin dashboard with real stats, charts, user management table
- [x] Admin controls: enable/disable users, extend trials, manage credits
- [x] User dashboard with info cards
- [x] CSV/Excel file upload with analytics (parsing, stats, sample data)
- [x] File analytics modal with columns info, data types, sample data
- [x] Report download (PDF/Excel) functionality
- [x] Integrations modal with browsable integrations list
- [x] Landing page with pricing, testimonials, how-it-works sections
- [x] Database seeding script with admin user
- [x] Fixed: Frontend compilation error (missing jspdf-autotable)
- [x] Fixed: Admin dashboard inaccessible (missing role field in seed)
- [x] Fixed: Auth module connection leak (refactored to shared db)
- [x] Fixed: ForgotPassword duplicate field + typo

### Mocked/Placeholder
- Connected data sources on user dashboard (using mock data)
- AI Visibility insights (hardcoded mock data)
- Forgot Password backend (uses setTimeout, no real email)

## Architecture
```
/app/backend/
  server.py          - FastAPI main app
  auth.py            - JWT auth, password hashing, RBAC
  models.py          - Pydantic models
  seed_database.py   - Database seeder
  routes/
    auth_routes.py   - /api/auth/*
    admin_routes.py  - /api/admin/*
    admin_management_routes.py - /api/admin/manage/*
    data_source_routes.py - /api/data-sources/*
    integration_routes.py - /api/integrations/*

/app/frontend/src/
  App.js             - Router
  pages/             - Login, Signup, UserDashboard, AdminDashboard, etc.
  services/api.js    - Axios API client
  mock/mockData.js   - Mock data for placeholders
  utils/reportExport.js - PDF/Excel report generation
```

## DB Schema
- `users`: name, email, password, role, plan, status, credits, created_at
- `subscriptions`: user_id, plan, status, amount, start_date, end_date
- `uploaded_files`: user_id, filename, analytics, sample_data, status
- `integrations`: user_id, integration_name, credentials, status

## Credentials
- Admin: admin@papermap.com / admin123
- Test User: testuser@analiyx.com / test1234

## Backlog (Prioritized)
### P1 - High Priority
- [ ] Google Ads & Meta Ads integration (OAuth flow, connect buttons)
- [ ] Google Sign-In integration
- [ ] Forgot Password backend flow (email sending)

### P2 - Medium Priority
- [ ] AI Visibility feature (LLM-powered URL analysis)
- [ ] Zoho Books & Google Sheets integrations
- [ ] Payment Gateway (Cashfree/Razorpay)
- [ ] Welcome email on signup

### P3 - Lower Priority
- [ ] Replace mock connected sources with real integration data
- [ ] AI-powered data analysis engine
- [ ] Refactor UserDashboard.jsx into smaller components
