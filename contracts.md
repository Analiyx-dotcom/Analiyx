# API Contracts & Backend Implementation Plan

## 1. Mocked Data to Replace

### From mockData.js:
- **testimonials**: Static testimonials (will remain static for now)
- **integrations**: Static integration list (will remain static for now)
- **pricingPlans**: Static pricing plans (will remain static for now)
- **trustedBrands**: Static brand names (will remain static for now)
- **howItWorks**: Static steps (will remain static for now)
- **adminStats**: Will fetch from database (user count, subscriptions, revenue, data sources)
- **recentUsers**: Will fetch from users collection
- **chartData**: Will calculate from database (user growth, revenue over time)

## 2. Database Models

### User Model
```javascript
{
  _id: ObjectId,
  name: String,
  email: String (unique),
  password: String (hashed),
  plan: String (enum: ['Hobby', 'Business Essential', 'Business Pro', 'Ultra']),
  status: String (enum: ['active', 'inactive']),
  credits: Number,
  createdAt: Date,
  updatedAt: Date
}
```

### Subscription Model
```javascript
{
  _id: ObjectId,
  userId: ObjectId (ref: User),
  plan: String,
  status: String (enum: ['active', 'cancelled', 'expired']),
  amount: Number,
  startDate: Date,
  endDate: Date,
  createdAt: Date
}
```

### DataSource Model
```javascript
{
  _id: ObjectId,
  userId: ObjectId (ref: User),
  name: String,
  type: String (PostgreSQL, MySQL, MongoDB, etc.),
  status: String (enum: ['connected', 'disconnected']),
  createdAt: Date
}
```

## 3. API Endpoints

### Authentication
- **POST /api/auth/register** - Register new user
  - Body: { name, email, password }
  - Returns: { token, user }

- **POST /api/auth/login** - Login user
  - Body: { email, password }
  - Returns: { token, user }

- **GET /api/auth/me** - Get current user
  - Headers: { Authorization: Bearer <token> }
  - Returns: { user }

### Admin Dashboard
- **GET /api/admin/stats** - Get dashboard statistics
  - Headers: { Authorization: Bearer <token> }
  - Returns: { totalUsers, activeSubscriptions, monthlyRevenue, dataSources }

- **GET /api/admin/users** - Get all users (paginated)
  - Headers: { Authorization: Bearer <token> }
  - Query: { page, limit }
  - Returns: { users[], total, page, totalPages }

- **GET /api/admin/charts/user-growth** - Get user growth data
  - Headers: { Authorization: Bearer <token> }
  - Returns: { data: [{ month, users }] }

- **GET /api/admin/charts/revenue** - Get revenue trend data
  - Headers: { Authorization: Bearer <token> }
  - Returns: { data: [{ month, amount }] }

### User Management
- **GET /api/users/:id** - Get user by ID
- **PUT /api/users/:id** - Update user
- **DELETE /api/users/:id** - Delete user

## 4. Frontend Integration Changes

### Auth Pages (Login.jsx, Signup.jsx)
- Replace mock authentication with actual API calls
- Use axios to call /api/auth/login and /api/auth/register
- Store JWT token in localStorage
- Handle validation errors from backend

### Admin Dashboard (AdminDashboard.jsx)
- Replace adminStats mock with API call to /api/admin/stats
- Replace recentUsers mock with API call to /api/admin/users
- Replace chartData mock with API calls to /api/admin/charts/user-growth and /api/admin/charts/revenue
- Add useEffect hooks to fetch data on component mount
- Add loading states

### Protected Routes
- Create ProtectedRoute component to check authentication
- Redirect to /login if no token found
- Verify token with backend on app load

## 5. Implementation Steps

1. Install backend dependencies (bcrypt, jsonwebtoken)
2. Create models (User, Subscription, DataSource)
3. Create auth middleware for JWT verification
4. Implement auth endpoints (register, login, me)
5. Implement admin endpoints (stats, users, charts)
6. Seed database with sample data for demo
7. Update frontend to use actual API endpoints
8. Test authentication flow
9. Test admin dashboard data fetching

## 6. Security Considerations
- Hash passwords with bcrypt (salt rounds: 10)
- JWT token expiry: 7 days
- Validate all inputs
- Sanitize database queries
- CORS properly configured
