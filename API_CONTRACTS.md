# Analiyx — API Contracts for Dashboard Integrations

> **For: External Developer**  
> This document describes the exact JSON response schemas that each dashboard endpoint must return.  
> The frontend components consume these shapes directly. When replacing sample data with real API calls, ensure your responses match these contracts exactly.

---

## Authentication

All endpoints require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

The backend extracts the `user_id` from the token via the `get_current_user_id` dependency.

---

## 1. Google Analytics — `GET /api/google-analytics/report`

**Query Params** (optional):
- `property_id` — GA4 property ID (auto-discovered if omitted)
- `days` — Number of days to look back (default: `30`)

**Response Schema:**

```json
{
  "is_sample_data": false,
  "property_id": "123456789",
  "summary": {
    "total_sessions": 14520,
    "total_users": 10234,
    "total_pageviews": 38900,
    "avg_bounce_rate": 48.3,
    "avg_session_duration": 142
  },
  "daily_metrics": [
    {
      "date": "Apr 01",
      "sessions": 520,
      "users": 380,
      "pageviews": 1240,
      "bounce_rate": 45.2,
      "avg_duration": 135,
      "new_users": 180
    }
  ],
  "top_pages": [
    {
      "page": "/pricing",
      "pageviews": 2180,
      "avg_time": "3m 42s"
    }
  ],
  "traffic_sources": [
    {
      "source": "Google / organic",
      "sessions": 5200,
      "percentage": 42
    }
  ]
}
```

**Notes:**
- `daily_metrics[]` should have one entry per day.
- `date` format: `"MMM DD"` (e.g., `"Apr 01"`).
- `avg_duration` is in seconds.
- `bounce_rate` is a percentage (0–100).

---

## 2. Google Ads — `GET /api/google-ads/campaigns`

**Query Params** (optional):
- `customer_id` — Google Ads customer ID (auto-discovered if omitted)

**Response Schema:**

```json
{
  "is_sample_data": false,
  "customer_id": "1234567890",
  "campaigns": [
    {
      "name": "Brand Search - Exact Match",
      "status": "ENABLED",
      "channel": "SEARCH",
      "impressions": 42500,
      "clicks": 3820,
      "ctr": 8.99,
      "avg_cpc": 12.40,
      "cost": 47368,
      "conversions": 285,
      "conv_value": 712500
    }
  ],
  "summary": {
    "total_impressions": 743900,
    "total_clicks": 26266,
    "total_cost": 182369,
    "total_conversions": 1260,
    "avg_ctr": 3.53,
    "avg_cpc": 6.94
  }
}
```

**Notes:**
- `status`: One of `"ENABLED"`, `"PAUSED"`, `"REMOVED"`.
- `channel`: One of `"SEARCH"`, `"DISPLAY"`, `"SHOPPING"`, `"VIDEO"`, `"PERFORMANCE_MAX"`.
- `cost` and `avg_cpc` are in the account's currency (INR for Indian accounts).
- `ctr` is a percentage (0–100).

---

## 3. Meta Ads — `GET /api/meta-ads/report`

**Response Schema:**

```json
{
  "is_sample_data": false,
  "summary": {
    "total_impressions": 609620,
    "total_reach": 483300,
    "total_clicks": 14525,
    "total_spend": 84900,
    "total_conversions": 842,
    "avg_ctr": 2.38,
    "avg_cpc": 5.85,
    "avg_cpm": 139.27
  },
  "daily_performance": [
    {
      "date": "Apr 01",
      "impressions": 18000,
      "reach": 14200,
      "clicks": 520,
      "spend": 2800,
      "conversions": 28
    }
  ],
  "campaigns": [
    {
      "name": "Brand Awareness - Instagram",
      "status": "ACTIVE",
      "objective": "BRAND_AWARENESS",
      "impressions": 185420,
      "reach": 142300,
      "clicks": 4215,
      "spend": 28500,
      "ctr": 2.27,
      "cpc": 6.76
    }
  ],
  "age_breakdown": [
    {
      "age_group": "18-24",
      "impressions": 125000,
      "clicks": 3800,
      "spend": 18500
    }
  ],
  "platform_breakdown": [
    {
      "platform": "Facebook",
      "value": 58
    }
  ]
}
```

**Notes:**
- `status`: One of `"ACTIVE"`, `"PAUSED"`.
- `objective`: Meta campaign objectives like `"BRAND_AWARENESS"`, `"LEAD_GENERATION"`, `"CONVERSIONS"`, `"VIDEO_VIEWS"`, `"LINK_CLICKS"`.
- `platform_breakdown[].value` is a percentage of total spend/impressions.

---

## 4. Google Sheets — `GET /api/google-sheets/report`

**Response Schema:**

```json
{
  "is_sample_data": false,
  "total_sheets": 2,
  "sheets": [
    {
      "spreadsheet_id": "1BxiMVs...",
      "title": "Monthly Sales Report",
      "last_modified": "2026-04-10T14:30:00Z",
      "sheet_count": 3,
      "row_count": 245,
      "preview_data": {
        "headers": ["Month", "Revenue", "Orders", "Avg Order Value", "Growth %"],
        "rows": [
          ["Jan 2026", "₹4,52,000", "128", "₹3,531", "+12%"]
        ]
      },
      "chart_data": [
        { "name": "Jan", "revenue": 452000, "orders": 128 }
      ]
    }
  ]
}
```

**Notes:**
- `chart_data` is flexible. If the first object has a `revenue` key, a bar chart is rendered. Otherwise, a pie chart is used with `name` + `value` keys.
- `preview_data.rows` is an array of arrays (each row = array of cell strings).
- `last_modified` should be ISO 8601.

---

## 5. Shopify — `GET /api/shopify/report`

**Response Schema:**

```json
{
  "is_sample_data": false,
  "store_name": "My Store",
  "summary": {
    "total_orders": 1420,
    "total_revenue": 4250000.00,
    "total_visitors": 52000,
    "avg_order_value": 2992.96,
    "conversion_rate": 2.73,
    "returning_customer_rate": 34.2,
    "cart_abandonment_rate": 68.5
  },
  "daily_performance": [
    {
      "date": "Apr 01",
      "orders": 48,
      "revenue": 145200.50,
      "visitors": 1800,
      "add_to_cart": 198,
      "conversion_rate": 2.67
    }
  ],
  "top_products": [
    {
      "name": "Premium Wireless Earbuds",
      "sku": "SKU-001",
      "sold": 342,
      "revenue": 854658,
      "inventory": 128,
      "status": "active"
    }
  ],
  "recent_orders": [
    {
      "order_id": "#AN-4521",
      "customer": "Priya M.",
      "items": 3,
      "total": 4580,
      "status": "fulfilled",
      "date": "2026-04-14"
    }
  ],
  "traffic_sources": [
    {
      "source": "Organic Search",
      "visitors": 4200,
      "percentage": 35
    }
  ]
}
```

**Notes:**
- `top_products[].status`: One of `"active"`, `"out_of_stock"`, `"low_stock"`.
- `recent_orders[].status`: One of `"fulfilled"`, `"processing"`, `"shipped"`, `"refunded"`.
- `date` format in `daily_performance`: `"MMM DD"` (e.g., `"Apr 01"`).
- Revenue/amounts are in INR.

---

## 6. Zoho Books — `GET /api/zoho/books/report`

**Response Schema:**

```json
{
  "is_sample_data": false,
  "module": "books",
  "summary": {
    "total_income": 3250000.00,
    "total_expenses": 2150000.00,
    "net_profit": 1100000.00,
    "profit_margin": 33.8,
    "total_invoiced": 574000,
    "paid_invoices": 470500,
    "overdue_amount": 42500,
    "accounts_receivable": 103500
  },
  "monthly_performance": [
    {
      "month": "Nov 2025",
      "income": 520000.00,
      "expenses": 345000.00,
      "profit": 175000.00
    }
  ],
  "invoices": [
    {
      "invoice_id": "INV-2026-0412",
      "customer": "TechFlow Solutions",
      "amount": 85000,
      "status": "paid",
      "due_date": "2026-04-20",
      "issue_date": "2026-03-20"
    }
  ],
  "expense_categories": [
    {
      "category": "Salaries & Wages",
      "amount": 285000,
      "percentage": 38
    }
  ]
}
```

**Notes:**
- `invoices[].status`: One of `"paid"`, `"overdue"`, `"sent"`, `"draft"`.
- `monthly_performance[].month` format: `"MMM YYYY"` (e.g., `"Nov 2025"`).

---

## 7. Zoho CRM — `GET /api/zoho/crm/report`

**Response Schema:**

```json
{
  "is_sample_data": false,
  "module": "crm",
  "summary": {
    "total_pipeline_value": 10310000,
    "total_deals_won": 4520000,
    "active_deals": 62,
    "win_rate": 71.4,
    "avg_deal_size": 301333.33,
    "total_leads": 451
  },
  "pipeline_stages": [
    {
      "stage": "Qualification",
      "deals": 24,
      "value": 1850000
    }
  ],
  "recent_deals": [
    {
      "deal_name": "Enterprise License - TechFlow",
      "stage": "Negotiation",
      "amount": 450000,
      "probability": 75,
      "close_date": "2026-04-30",
      "owner": "Anil K."
    }
  ],
  "monthly_deals": [
    {
      "month": "Nov",
      "won": 8,
      "lost": 3,
      "value_won": 2100000
    }
  ],
  "lead_sources": [
    {
      "source": "Website",
      "leads": 145,
      "percentage": 32
    }
  ]
}
```

**Notes:**
- `pipeline_stages[].stage`: Values are `"Qualification"`, `"Needs Analysis"`, `"Proposal"`, `"Negotiation"`, `"Closed Won"`, `"Closed Lost"`.
- The pipeline bar chart uses `value` for the bar width and colors `Closed Won` green, `Closed Lost` red.

---

## Common Patterns

### `is_sample_data` Flag
Every endpoint includes `"is_sample_data": true/false`. Set to `false` when returning real data. The frontend uses this to display a yellow "Sample Data" badge.

### Error Handling
If a connection is not available, the endpoint should still return the sample data structure with `"is_sample_data": true` — **do not throw a 4xx error**. This allows the UI to always render gracefully.

### Currency
All monetary values are in INR (Indian Rupees). The frontend formats them with `₹` prefix and Indian locale grouping.
