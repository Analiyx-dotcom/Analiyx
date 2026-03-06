# Analiyx - Remaining Implementation Guide

## ✅ Completed (Phase 1)
1. ✅ Forgot Password page UI (needs email service for actual functionality)
2. ✅ Email uniqueness verification (already in backend)
3. ✅ Social media links in footer
4. ✅ INR Pricing with 3 plans (₹1,599, ₹4,999, Custom)
5. ✅ Admin login URL: `/admin` | Email: `admin@papermap.com` | Password: `admin123`
6. ✅ Separate admin dashboard (already working)
7. ✅ Black theme with white logo (already implemented)

---

## 🔧 Phase 2: Integrations Needed

### 1. Google OAuth Login
**Status**: Needs Google Cloud credentials

**Steps to Get Credentials:**
1. Go to: https://console.cloud.google.com/
2. Create new project: "Analiyx"
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized redirect URIs:
   - `https://analiyx.com/auth/google/callback`
   - `http://localhost:3000/auth/google/callback` (for testing)
7. Copy Client ID and Client Secret

**Required from you:**
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET

---

### 2. Welcome Email Service
**Status**: Needs email service provider

**Recommended Options:**

**Option A: SendGrid (Easiest)**
- Free tier: 100 emails/day
- Setup: https://sendgrid.com/
- Get API key from Settings → API Keys

**Option B: Gmail SMTP (Quick setup)**
- Use your Gmail account
- Enable "App Password" in Google Account settings

**Option C: AWS SES (Scalable)**
- Production-grade
- Very cheap ($0.10 per 1000 emails)

**Required from you:**
- Email service choice
- API key/credentials
- Sender email (e.g., welcome@analiyx.com)

---

### 3. Payment Gateway Integration

**Option A: Cashfree (Recommended for India)**
- Sign up: https://www.cashfree.com/
- Get credentials from Dashboard → Developers → API Keys
- Test mode vs Production mode

**Option B: Razorpay**
- Sign up: https://dashboard.razorpay.com/
- Get API keys from Settings → API Keys

**Required from you:**
- Gateway choice (Cashfree or Razorpay)
- Client ID / API Key
- Client Secret / API Secret
- Webhook secret (for payment confirmations)

---

## 🎯 Phase 3: Admin Management Features

### Features to Implement:
1. **User Management**
   - Enable/disable user accounts
   - Extend trial periods
   - View user activity logs

2. **Credits Management**
   - Add credits to user account
   - Remove/deduct credits
   - Edit credit balance
   - View credit usage history

3. **Subscription Management**
   - View payment history
   - Manual plan upgrades/downgrades
   - Refund management
   - Subscription pause/resume

4. **Payment Dashboard**
   - Total revenue analytics
   - Recent transactions list
   - Failed payment tracking
   - Export payment reports

---

## 📋 Implementation Checklist

### Immediate Actions Needed:
- [ ] Decide on Email Service (SendGrid/Gmail/AWS SES)
- [ ] Decide on Payment Gateway (Cashfree/Razorpay)
- [ ] Get Google OAuth credentials
- [ ] Provide actual social media URLs (currently placeholder)
- [ ] Decide on sender email address

### Once You Provide API Keys:
- [ ] Implement Google Login (30 mins)
- [ ] Implement Welcome Email (20 mins)
- [ ] Implement Payment Gateway (1-2 hours)
- [ ] Add Admin Management UI (2-3 hours)
- [ ] Add Admin API endpoints (1-2 hours)
- [ ] Test complete flow (1 hour)

---

## 🚀 Next Steps

**Please provide:**
1. **Google OAuth**
   ```
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_secret_here
   ```

2. **Email Service**
   ```
   EMAIL_SERVICE=sendgrid (or gmail or aws_ses)
   EMAIL_API_KEY=your_api_key_here
   SENDER_EMAIL=welcome@analiyx.com
   ```

3. **Payment Gateway**
   ```
   PAYMENT_GATEWAY=cashfree (or razorpay)
   PAYMENT_CLIENT_ID=your_client_id_here
   PAYMENT_CLIENT_SECRET=your_secret_here
   PAYMENT_WEBHOOK_SECRET=your_webhook_secret_here
   ```

4. **Social Media Links** (optional)
   ```
   FACEBOOK_URL=https://facebook.com/yourpage
   TWITTER_URL=https://twitter.com/yourhandle
   LINKEDIN_URL=https://linkedin.com/company/yourcompany
   INSTAGRAM_URL=https://instagram.com/yourhandle
   ```

Once you provide these, I'll implement all remaining features!

---

## 📞 Support

If you need help getting any of these credentials, let me know and I can guide you through the setup process for each service.
