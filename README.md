# Analiyx - Big Data for Small Teams

AI-powered no-code data analytics platform for lean teams.

## 🚀 Features

- **Dark Theme UI** - Modern, sleek interface
- **JWT Authentication** - Secure role-based access control
- **Admin Dashboard** - Analytics, user management, revenue tracking
- **User Dashboard** - Personal analytics workspace
- **Indian Localization** - Ready for Indian market
- **Role-Based Access** - Separate admin and user experiences

## 🛠️ Tech Stack

### Frontend
- React 19
- Shadcn UI Components
- Tailwind CSS
- Axios for API calls
- React Router DOM

### Backend
- FastAPI (Python)
- MongoDB (Motor async driver)
- JWT Authentication with bcrypt
- Role-based authorization

## 📦 Installation

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB 6.0+
- Yarn package manager

### Frontend Setup
```bash
cd frontend
yarn install
yarn start
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python seed_database.py  # Seed initial data
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

## 🔐 Default Admin Credentials
- Email: admin@papermap.com
- Password: admin123

## 🌍 Environment Variables

### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=analiyx_db
JWT_SECRET_KEY=your-secret-key-here
```

## 📱 Routes

- `/` - Landing page
- `/login` - User/Admin login
- `/signup` - User registration
- `/dashboard` - User dashboard
- `/admin` - Admin panel (restricted)

## 🏗️ Project Structure

```
/app
├── frontend/          # React application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── mock/        # Mock data
│   └── public/
├── backend/           # FastAPI application
│   ├── routes/        # API routes
│   ├── models.py      # Pydantic models
│   ├── auth.py        # Authentication logic
│   ├── server.py      # Main FastAPI app
│   └── seed_database.py
└── contracts.md       # API contracts
```

## 🚀 Deployment

See deployment guide in repository for production setup instructions.

## 📄 License

MIT License

---

Built with ❤️ for the Indian market
