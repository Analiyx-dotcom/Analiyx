from fastapi import APIRouter, HTTPException, Depends
from models import UserCreate, UserLogin, AuthResponse, UserResponse
from auth import hash_password, verify_password, create_access_token, get_current_user_id
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Database will be injected
db = None

def set_database(database):
    global db
    db = database

@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user document - 7 day trial with Trial plan
    user_doc = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "plan": "Trial",
        "status": "active",
        "credits": 50,
        "role": "user",
        "trial_ends_at": datetime.utcnow() + timedelta(days=7),
        "subscription_end_date": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert user
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Create access token
    token = create_access_token({"user_id": str(result.inserted_id)})
    
    # Return response
    user_response = UserResponse(
        id=str(user_doc["_id"]),
        name=user_doc["name"],
        email=user_doc["email"],
        plan=user_doc["plan"],
        status=user_doc["status"],
        credits=user_doc["credits"],
        role=user_doc["role"],
        trial_ends_at=user_doc.get("trial_ends_at"),
        subscription_end_date=user_doc.get("subscription_end_date"),
        created_at=user_doc["created_at"]
    )
    
    # Send welcome email (non-blocking)
    try:
        from email_service import send_welcome_email
        send_welcome_email(user_data.email, user_data.name)
    except Exception:
        pass

    return AuthResponse(token=token, user=user_response)

@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """Login user"""
    # Find user by email
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # STRICTLY block disabled, inactive, or spam accounts
    user_status = user.get("status", "active")
    if user_status in ("disabled", "inactive", "spam"):
        if user_status == "spam":
            raise HTTPException(status_code=403, detail="Your account has been blocked for spam. Contact support at techmeliora@gmail.com")
        raise HTTPException(status_code=403, detail="Your account has been disabled. Contact support at techmeliora@gmail.com")
    
    # Create access token
    token = create_access_token({"user_id": str(user["_id"])})
    
    # Return response
    user_response = UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        plan=user["plan"],
        status=user["status"],
        credits=user["credits"],
        role=user.get("role", "user"),
        trial_ends_at=user.get("trial_ends_at"),
        subscription_end_date=user.get("subscription_end_date"),
        created_at=user["created_at"]
    )
    
    return AuthResponse(token=token, user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current authenticated user - blocks disabled/spam users"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Block disabled/spam users even with valid token
    user_status = user.get("status", "active")
    if user_status in ("disabled", "inactive", "spam"):
        if user_status == "spam":
            raise HTTPException(status_code=403, detail="Your account has been blocked for spam. Contact support.")
        raise HTTPException(status_code=403, detail="Your account has been disabled. Contact support.")
    
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        plan=user["plan"],
        status=user["status"],
        credits=user["credits"],
        role=user.get("role", "user"),
        trial_ends_at=user.get("trial_ends_at"),
        subscription_end_date=user.get("subscription_end_date"),
        created_at=user["created_at"]
    )