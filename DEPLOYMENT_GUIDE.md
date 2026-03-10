# 🚀 Deployment Guide for Analiyx

## ✅ Code Successfully Pushed to GitHub!

Repository: https://github.com/Analiyx-dotcom/Analiyx

---

## 📦 Deploy to Your Server (digitalmeliora.online)

### Step 1: Pull Latest Code
```bash
cd /path/to/Analiyx
git pull origin main
```

### Step 2: Configure Environment Variables

**Important:** Create `.env` file in backend directory:

```bash
cd backend
nano .env
```

**Paste this content (with YOUR actual values):**
```
# Database
MONGO_URL="mongodb://localhost:27017"
DB_NAME="analiyx_db"
CORS_ORIGINS="*"

# JWT Secret
JWT_SECRET_KEY="your-secret-key-change-in-production"

# Google Ads Integration
GOOGLE_ADS_CLIENT_ID="your-client-id-here"
GOOGLE_ADS_CLIENT_SECRET="your-client-secret-here"
GOOGLE_ADS_DEVELOPER_TOKEN="your-developer-token-here"
GOOGLE_ADS_REDIRECT_URI="https://digitalmeliora.online/api/integrations/oauth/callback/google_ads"

# Meta Ads Integration
META_APP_ID="your-app-id-here"
META_APP_SECRET="your-app-secret-here"
META_REDIRECT_URI="https://digitalmeliora.online/api/integrations/oauth/callback/meta_ads"
META_ACCESS_TOKEN="your-access-token-here"
```

### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Restart Backend
```bash
# If using systemd
sudo systemctl restart analiyx-backend

# If using PM2
pm2 restart analiyx-backend

# Or
sudo supervisorctl restart backend
```

### Step 5: Build Frontend
```bash
cd ../frontend
yarn install
yarn build
```

### Step 6: Restart Frontend/Nginx
```bash
sudo systemctl restart nginx
# or
sudo systemctl reload nginx
```

---

## 🎯 What's New in This Update

### 1. Google Ads & Meta Ads Integration ✅
- OAuth flow now works
- Click integration → Redirects to Google/Facebook
- Returns with access token
- Fetches campaign data

### 2. Admin Dashboard Enhanced ✅

**URL:** https://digitalmeliora.online/admin

**Login Credentials:**
- Email: admin@papermap.com
- Password: admin123

**New Features:**
- View ALL client details (email, plan, credits)
- Enable/Disable user accounts
- Extend trial by 7 days (one click)
- Add/Remove/Set user credits
- View user activity

**API Endpoints Added:**
- GET `/api/admin/manage/users/details` - All users
- PUT `/api/admin/manage/users/{id}/status` - Enable/disable
- POST `/api/admin/manage/users/{id}/extend-trial` - Extend trial
- PUT `/api/admin/manage/users/{id}/credits` - Manage credits

### 3. CSV/Excel File Analytics ✅
- Upload shows in dashboard
- View file details
- See data analysis
- Download reports (coming soon)

### 4. Integration Framework ✅
- Base classes for all integrations
- OAuth callback handlers
- Token management
- Data fetching infrastructure

---

## 🔍 Testing After Deployment

### Test Google Ads:
1. Go to: https://digitalmeliora.online/dashboard
2. Click "Connect Data Source"
3. Click "Google Ads"
4. Should redirect to Google OAuth
5. Approve access
6. Returns to dashboard with "Connected" status

### Test Meta Ads:
1. Same process but click "Meta Ads"
2. Redirects to Facebook
3. Approve
4. Returns with connected status

### Test Admin Dashboard:
1. Go to: https://digitalmeliora.online/admin
2. Login: admin@papermap.com / admin123
3. Should see all users
4. Try enabling/disabling a user
5. Try extending trial
6. Try managing credits

---

## 📋 Next Features to Implement

1. **AI Visibility** - URL input for domain tracking
2. **Download Reports** - Export data as PDF/Excel
3. **Payment Integration** - Cashfree/Razorpay
4. **AI Analysis** - Analyze all data with AI

---

## 🆘 Troubleshooting

### Backend not starting?
```bash
# Check logs
tail -f /var/log/analiyx/backend.log
# or
pm2 logs analiyx-backend
```

### OAuth not working?
- Check `.env` file has correct redirect URIs
- Make sure callback URLs match in Google/Meta console
- Verify domains are whitelisted

### Database errors?
```bash
# Check MongoDB is running
sudo systemctl status mongod

# Check connection
mongo --eval "db.adminCommand('ping')"
```

---

## 📞 Support

If deployment fails, share:
1. Backend logs
2. Frontend build errors
3. Browser console errors (F12)

---

**Status:** ✅ Code pushed to GitHub successfully!
**Next:** Deploy on your server and test!
