# Analiyx - Product Requirements Document

## Original Problem Statement
Build a dark-themed analytics platform "Analiyx" (clone of papermap.ai) with user/admin dashboards, trial system, plan-based restrictions, and AI-powered data analysis. Enhanced to become an enterprise-grade AI Analytics Platform with Metadata Engine, Semantic Search, Query Planner, and Live Query Engine.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn/ui, Recharts, @nangohq/frontend
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic, Nango SDK
- **AI**: GPT-5.2 via emergentintegrations (Emergent LLM Key)
- **Payments**: Razorpay (Live keys)
- **OAuth**: Nango (managed OAuth)
- **Database**: MongoDB (primary), Redis (cache), PostgreSQL/MySQL (external connectors)
- **Cache**: Redis (localhost:6379)

## Pricing Plans
- **Trial**: Free 7 days, 100 credits (one-time)
- **Starter**: ₹9,999/year, 200 credits/month
- **Business Pro**: ₹14,999/year, 500 credits/month

## Implemented Features

### Enterprise Data Engine (NEW - July 2026)
- [x] Modular service architecture: `/backend/services/` (connectors, metadata, semantic, query, cache)
- [x] Database Connectors: PostgreSQL and MySQL via asyncpg/aiomysql
- [x] Datasource Management: Connect, test, list, update, delete external databases
- [x] Metadata Scanner: Scan schemas, tables, columns from external databases
- [x] Metadata Profiler: Profile columns (nulls, distinct values, min/max, distributions)
- [x] AI Enrichment: Generate business descriptions for tables using GPT-5.2
- [x] Semantic Search: NL search over metadata with AI interpretation
- [x] Business Glossary: CRUD for business terms mapped to technical metadata
- [x] Query Planner: Natural language to SQL via GPT-5.2 with schema context
- [x] SQL Validator: Safety validation (blocks DROP/DELETE/INSERT/etc)
- [x] Query Executor: Live/Cached/Hybrid execution modes
- [x] Redis Cache: Query result caching with TTL
- [x] Background Jobs: Async metadata scanning, profiling, enrichment
- [x] Frontend: Full Data Engine page at /data-engine with 6 tabs
- [x] 21 backend tests passing (test_enterprise_data_engine.py)

### Google Ads Integration (via Nango)
- [x] Connect Google Ads button via Nango OAuth
- [x] Backend: GET /api/google-ads/customers (list accessible customer IDs)
- [x] Backend: GET /api/google-ads/campaigns (GAQL query for campaigns with metrics)
- [x] Frontend: GoogleAdsDashboard component with 4 summary cards
- [x] Frontend: CampaignsTable showing name, status, type, budget, metrics

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

## Architecture

```
/app/backend/
├── services/
│   ├── connectors/     # PostgreSQL, MySQL connectors
│   │   ├── base.py     # Abstract connector interface
│   │   ├── postgresql.py
│   │   ├── mysql.py
│   │   └── factory.py  # Connector factory
│   ├── metadata/       # Scanner, Profiler, Embeddings
│   ├── semantic/       # Search, Glossary
│   ├── query/          # Planner, Validator, Executor
│   ├── cache/          # Redis cache service
│   └── background_tasks.py
├── routes/
│   ├── datasource_connect_routes.py  # /api/datasources/*
│   ├── metadata_routes.py            # /api/metadata/*
│   ├── semantic_routes.py            # /api/semantic/*
│   ├── query_routes.py               # /api/query/*
│   └── ... (existing routes)
└── tests/
    └── test_enterprise_data_engine.py

/app/frontend/src/
├── pages/
│   ├── DataEngine.jsx   # Enterprise Data Engine UI (6 tabs)
│   └── ... (existing pages)
└── services/
    └── api.js           # Added datasourceAPI, metadataAPI, semanticAPI, queryAPI
```

## Credentials
- Admin: Admin@analiyx.com / 1234
- Test: testuser@test.com / test1234
- Nango Secret: ae6ff9d5-8289-4a48-baa3-b80e9e1f6c0f

## Known Issues
- Gmail SMTP BLOCKED (Google rejecting app passwords)
- Google Analytics 403 Scopes via Nango (needs Nango dashboard config)

## Backlog
### P1
- [ ] Chart color theme selector (6 themes)
- [ ] Bookmark chat messages to Notes
- [ ] Monthly credit reset cron

### P2
- [ ] Social Logins, Editable Dashboard
- [ ] Rate limiting on public endpoints

### P3
- [ ] Email Verification, Forgot Password backend
- [ ] Refactor UserDashboard.jsx into smaller components
- [ ] Add aria-describedby to Dialog components for accessibility
