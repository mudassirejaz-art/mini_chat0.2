from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse  # <-- Add JSONResponse here
from sqlalchemy.orm import Session
from app.schemas import *
from app.models import User
from app.auth import *
from app.email_utils import send_verification_email
from app.database import get_db
import logging
import jwt

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------- Signup ----------------
@router.post("/signup", response_model=SignupResponse)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pwd = hash_password(data.password)
    new_user = User(email=data.email, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_jwt_token({"user_id": new_user.id})
    print(f"[DEBUG] Generated token for {new_user.email}: {token}")

    # Send verification email
    send_verification_email(new_user.email, new_user.email, token)

    logger.info(f"New signup: {data.email}")
    return SignupResponse(
        status="success",
        message="User registered. Check your email to verify."
    )

# ---------------- Verify Email ----------------
@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return JSONResponse({"status": "error", "message": "Token expired"})
    except jwt.InvalidTokenError:
        return JSONResponse({"status": "error", "message": "Invalid token"})

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse({"status": "error", "message": "User not found"})

    if not user.is_verified:
        user.is_verified = True
        db.commit()
        logger.info(f"User verified: {user.email}")

    # Optional: return a message instead of redirect; frontend handles login redirect
    return JSONResponse({"status": "success", "message": "Email verified"})

from datetime import datetime, timedelta

# ---------------- Login ----------------
@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")
    
    access_token = create_jwt_token({"user_id": user.id})
    
    # Generate refresh token with 7 days expiration manually
    expire_time = datetime.utcnow() + timedelta(days=7)
    refresh_token = create_jwt_token({
        "user_id": user.id,
        "exp": expire_time
    })
    
    return LoginResponse(
        status="success",
        message="Login successful",
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

