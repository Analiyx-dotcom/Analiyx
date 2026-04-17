# Analiyx — Local Development Setup Guide

> For developers who want to run the project locally on their machine.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Node.js | 18+ | https://nodejs.org |
| Python | 3.10+ | https://python.org |
| MongoDB | 6.0+ | See below |
| Yarn | 1.22+ | `npm install -g yarn` |
| Git | Latest | https://git-scm.com |

---

## 1. Install MongoDB Locally

### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```

### Ubuntu/Debian
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update && sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Windows
1. Download from https://www.mongodb.com/try/download/community
2. Run the MSI installer (choose "Complete" setup)
3. Check "Install MongoDB as a Service"
4. MongoDB will start automatically

### Verify MongoDB is running
```bash
mongosh
# You should see the MongoDB shell. Type 'exit' to quit.
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/analiyx.git
cd analiyx
```

---

## 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### Create backend `.env` file

```bash
cp .env.example .env
```

Now edit `backend/.env` with your values. **Minimum required for local development:**

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=analiyx_db
CORS_ORIGINS=http://localhost:3000
JWT_SECRET_KEY=local-dev-secret-key-change-in-production
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
EMERGENT_LLM_KEY=your_emergent_key
NANGO_SECRET_KEY=your_nango_secret
NANGO_HOST=https://api.nango.dev
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
GOOGLE_ADS_CLIENT_ID=your_google_client_id
GOOGLE_ADS_CLIENT_SECRET=your_google_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_REDIRECT_URI=http://localhost:8001/api/integrations/oauth/callback/google_ads
GOOGLE_ANALYTICS_REDIRECT_URI=http://localhost:8001/api/integrations/oauth/callback/google_analytics
GOOGLE_SHEETS_REDIRECT_URI=http://localhost:8001/api/integrations/oauth/callback/google_sheets
GOOGLE_SHEETS_API_KEY=your_sheets_api_key
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_REDIRECT_URI=http://localhost:8001/api/integrations/oauth/callback/meta_ads
META_ACCESS_TOKEN=your_meta_access_token
```

> **Note:** If you don't have all API keys yet, the dashboards will still work — they return sample data automatically when integrations are not connected.

### Start Backend

```bash
cd backend
source venv/bin/activate   # or venv\Scripts\activate on Windows
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Default admin account created: Admin@analiyx.com / 1234
```

### Verify Backend

```bash
curl http://localhost:8001/api/health
# Should return: {"status":"ok","db":"connected","users":1}
```

---

## 4. Frontend Setup

Open a **new terminal** (keep backend running):

```bash
cd frontend

# Install dependencies
yarn install
```

### Create frontend `.env` file

```bash
cp .env.example .env
```

Edit `frontend/.env`:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Start Frontend

```bash
yarn start
```

The app will open at **http://localhost:3000**

---

## 5. Login Credentials

The backend automatically creates an admin account on first startup:

| Role | Email | Password |
|---|---|---|
| **Admin** | `Admin@analiyx.com` | `1234` |

To create a test user, sign up via the UI at http://localhost:3000/signup

Or use this existing test account (if database was seeded):

| Role | Email | Password |
|---|---|---|
| **Test User** | `testuser@test.com` | `test1234` |

---

## 6. MongoDB Details

| Setting | Value |
|---|---|
| **Connection URL** | `mongodb://localhost:27017` |
| **Database Name** | `analiyx_db` |
| **Auth Required?** | No (local default has no auth) |

### View Data with MongoDB Compass (GUI)

1. Download [MongoDB Compass](https://www.mongodb.com/try/download/compass)
2. Connect with: `mongodb://localhost:27017`
3. Select database: `analiyx_db`
4. Key collections: `users`, `workspaces`, `notes`, `reports`, `tickets`, `coupons`

### View Data with mongosh (CLI)

```bash
mongosh
use analiyx_db
db.users.find().pretty()
```

---

## 7. Project Structure

```
analiyx/
├── backend/
│   ├── server.py              # Main FastAPI app
│   ├── auth.py                # JWT authentication
│   ├── routes/                # All API routes
│   │   ├── shopify_routes.py  # Shopify dashboard data
│   │   ├── zoho_routes.py     # Zoho Books & CRM data
│   │   ├── meta_ads_routes.py # Meta Ads data
│   │   └── ...
│   ├── .env.example           # Template (committed)
│   └── .env                   # Your secrets (NOT committed)
├── frontend/
│   ├── src/
│   │   ├── components/        # Dashboard components
│   │   ├── pages/             # Page components
│   │   └── services/api.js    # API client
│   ├── .env.example           # Template (committed)
│   └── .env                   # Your config (NOT committed)
├── API_CONTRACTS.md           # JSON schemas for all dashboard endpoints
└── DEPLOY.md                  # VPS deployment guide
```

---

## 8. API Endpoints (Dashboard)

All dashboard endpoints return **sample data** by default. Replace with real API calls as needed.
See `API_CONTRACTS.md` for complete JSON response schemas.

| Endpoint | Description |
|---|---|
| `GET /api/google-analytics/report` | GA4 sessions, users, pageviews, traffic |
| `GET /api/google-ads/campaigns` | Google Ads campaigns & metrics |
| `GET /api/meta-ads/report` | Meta/Facebook Ads performance |
| `GET /api/google-sheets/report` | Connected spreadsheet data |
| `GET /api/shopify/report` | Store orders, revenue, products |
| `GET /api/zoho/books/report` | Invoices, income, expenses |
| `GET /api/zoho/crm/report` | Deals pipeline, leads, CRM data |

All endpoints require `Authorization: Bearer <token>` header.

---

## Troubleshooting

### "MongoDB connection refused"
```bash
# Check if MongoDB is running
sudo systemctl status mongod    # Linux
brew services list              # macOS
# Windows: Check Services app for "MongoDB Server"
```

### "Module not found" errors (backend)
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "CORS error" in browser
Make sure `backend/.env` has:
```
CORS_ORIGINS=http://localhost:3000
```
Then restart the backend.

### Frontend can't reach backend
Make sure `frontend/.env` has:
```
REACT_APP_BACKEND_URL=http://localhost:8001
```
Then restart the frontend (`yarn start`).
