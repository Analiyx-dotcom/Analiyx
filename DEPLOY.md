# Analiyx — VPS Deployment Guide (Hostinger KVM1)

## Prerequisites

| Requirement | Version |
|---|---|
| Ubuntu | 22.04+ |
| Node.js | 18+ |
| Python | 3.10+ |
| MongoDB | 6.0+ |
| Nginx | Latest |
| PM2 | Latest |
| Certbot | Latest |

---

## 1. Initial VPS Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential software-properties-common
```

---

## 2. Install Node.js 18+

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g yarn pm2
node -v && yarn -v && pm2 -v
```

---

## 3. Install Python 3.10+ & pip

```bash
sudo apt install -y python3 python3-pip python3-venv
python3 --version
```

---

## 4. Install MongoDB 6.0

```bash
# Import MongoDB GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor

# Add repo
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

sudo apt update && sudo apt install -y mongodb-org

# Start & enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
sudo systemctl status mongod
```

---

## 5. Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
```

---

## 6. Clone the Repository

```bash
sudo mkdir -p /var/www/analiyx
sudo chown $USER:$USER /var/www/analiyx
cd /var/www/analiyx
git clone https://github.com/YOUR_USERNAME/analiyx.git .
```

---

## 7. Backend Setup

```bash
cd /var/www/analiyx/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Create .env from example
cp .env.example .env
nano .env   # Fill in ALL your actual values
```

### Backend .env — Required Variables

| Variable | Description | Example |
|---|---|---|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | Database name | `analiyx_db` |
| `PORT` | Backend port | `8001` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `https://analiyx.com,https://www.analiyx.com` |
| `JWT_SECRET_KEY` | Random 64-char secret | `openssl rand -hex 32` |
| `RAZORPAY_KEY_ID` | Razorpay live key | `rzp_live_XXXXX` |
| `RAZORPAY_KEY_SECRET` | Razorpay secret | `axXXXXXXXXXX` |
| `NANGO_SECRET_KEY` | Nango secret (UUID) | `ae6ff9d5-xxxx-xxxx` |
| `NANGO_HOST` | Nango API host | `https://api.nango.dev` |
| `EMERGENT_LLM_KEY` | AI key for GPT-5.2 | `sk-emergent-XXXXX` |
| `SMTP_EMAIL` | Email for notifications | `your@gmail.com` |
| `SMTP_PASSWORD` | Gmail App Password | `xxxx xxxx xxxx xxxx` |

> **Generate JWT secret:** `openssl rand -hex 32`

### Test Backend Locally

```bash
source venv/bin/activate
cd /var/www/analiyx/backend
python3 server.py
# Should show: Uvicorn running on http://0.0.0.0:8001
# Press Ctrl+C to stop
```

---

## 8. Frontend Setup

```bash
cd /var/www/analiyx/frontend

# Create .env for production
cp .env.example .env
nano .env
```

### Frontend .env — Production

```env
# IMPORTANT: Leave empty for same-origin nginx deployment
REACT_APP_BACKEND_URL=
```

> When `REACT_APP_BACKEND_URL` is empty, API calls go to `/api/*` which nginx proxies to the backend. **This is the correct setup for VPS.**

```bash
# Install dependencies and build
yarn install
yarn build
```

The build output will be in `/var/www/analiyx/frontend/build/`.

---

## 9. Nginx Configuration

```bash
# Copy nginx config
sudo cp /var/www/analiyx/nginx.conf /etc/nginx/sites-available/analiyx

# Edit: Replace "yourdomain.com" with your actual domain
sudo nano /etc/nginx/sites-available/analiyx

# Enable site
sudo ln -sf /etc/nginx/sites-available/analiyx /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

---

## 10. SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
# Follow prompts, enter your email, agree to terms

# Auto-renewal test
sudo certbot renew --dry-run
```

---

## 11. Start Backend with PM2

```bash
cd /var/www/analiyx

# Create log directory
sudo mkdir -p /var/log/analiyx
sudo chown $USER:$USER /var/log/analiyx

# Start using PM2 with uvicorn (recommended)
cd /var/www/analiyx/backend
pm2 start "source /var/www/analiyx/backend/venv/bin/activate && uvicorn server:app --host 0.0.0.0 --port 8001 --workers 2" --name analiyx-backend

# Save PM2 config (survives reboot)
pm2 save
pm2 startup
# Run the command it outputs (sudo env PATH=...)
```

### Verify

```bash
pm2 status
pm2 logs analiyx-backend --lines 20

# Test API
curl http://localhost:8001/api/health
```

---

## 12. Firewall Setup

```bash
sudo ufw allow ssh         # Port 22
sudo ufw allow 80/tcp      # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
sudo ufw status
```

> **Do NOT expose port 8001 or 27017** — nginx proxies API traffic, and MongoDB should only accept local connections.

---

## 13. MongoDB Security (Optional but Recommended)

```bash
mongosh

use admin
db.createUser({
  user: "analiyx_admin",
  pwd: "YOUR_STRONG_PASSWORD",
  roles: [ { role: "readWrite", db: "analiyx_db" } ]
})
exit
```

Then update `/var/www/analiyx/backend/.env`:

```env
MONGO_URL=mongodb://analiyx_admin:YOUR_STRONG_PASSWORD@localhost:27017/analiyx_db?authSource=admin
```

Enable MongoDB auth in `/etc/mongod.conf`:

```yaml
security:
  authorization: enabled
```

```bash
sudo systemctl restart mongod
```

---

## Updating After Git Push

When you push new code from GitHub:

```bash
cd /var/www/analiyx

# Pull latest code
git pull origin main

# Backend: Update dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart analiyx-backend

# Frontend: Rebuild
cd ../frontend
yarn install
yarn build

# If nginx config changed:
sudo nginx -t && sudo systemctl reload nginx
```

### Quick Update Script

Save as `/var/www/analiyx/deploy.sh`:

```bash
#!/bin/bash
set -e
cd /var/www/analiyx

echo ">>> Pulling latest code..."
git pull origin main

echo ">>> Updating backend..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart analiyx-backend

echo ">>> Rebuilding frontend..."
cd ../frontend
yarn install
yarn build

echo ">>> Done! App is live."
```

```bash
chmod +x /var/www/analiyx/deploy.sh
# Run anytime: ./deploy.sh
```

---

## Troubleshooting

### Backend won't start
```bash
pm2 logs analiyx-backend --lines 50
# Check for missing env vars or import errors
```

### Frontend shows blank page
```bash
# Make sure build exists
ls /var/www/analiyx/frontend/build/index.html

# Check nginx config
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### API calls return 502
```bash
# Backend might be down
pm2 status
pm2 restart analiyx-backend

# Check if port 8001 is listening
sudo ss -tlnp | grep 8001
```

### MongoDB connection refused
```bash
sudo systemctl status mongod
sudo systemctl start mongod
```

### CORS errors in browser
```
Update CORS_ORIGINS in backend/.env to include your exact domain:
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
Then: pm2 restart analiyx-backend
```

---

## Architecture Summary

```
                    ┌─────────────┐
    Browser ──────► │   Nginx     │
    (HTTPS:443)     │  :80/:443   │
                    └──────┬──────┘
                           │
               ┌───────────┴───────────┐
               │                       │
        /api/* routes           / (all other)
               │                       │
    ┌──────────▼──────────┐  ┌─────────▼─────────┐
    │   FastAPI Backend   │  │  React Static      │
    │   (PM2 → :8001)     │  │  /frontend/build   │
    └──────────┬──────────┘  └────────────────────┘
               │
    ┌──────────▼──────────┐
    │     MongoDB         │
    │   localhost:27017   │
    └─────────────────────┘
```

---

## Ports Summary

| Port | Service | Exposed? |
|---|---|---|
| 22 | SSH | Yes (firewall) |
| 80 | Nginx HTTP | Yes (redirects to 443) |
| 443 | Nginx HTTPS | Yes |
| 8001 | FastAPI | No (internal only) |
| 27017 | MongoDB | No (internal only) |
