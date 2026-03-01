import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Get current user ID from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user_id

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Get current user with role information"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Fetch user from database to get role
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    from bson import ObjectId
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", "user")
    }

async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role for endpoint access"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Access forbidden. Admin privileges required."
        )
    return current_user