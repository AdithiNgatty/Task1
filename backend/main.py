from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import random, smtplib, os
from email.mime.text import MIMEText
from dotenv import load_dotenv

from backend.database import db
from backend.models import UserCreate, UserLogin, UserOut
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# Load environment variables
load_dotenv()

# Initialize app
app = FastAPI(title="FastAPI Auth with MongoDB + OTP")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- EMAIL CONFIG --------------------
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_otp_email(recipient_email: str, otp: str):
    """Send OTP to user’s email."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise HTTPException(status_code=500, detail="Email not configured")

    subject = "Your OTP Verification Code"
    body = f"Your OTP code is: {otp}\n\nIt will expire in 5 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("❌ Email sending failed:", e)
        raise HTTPException(status_code=500, detail="Failed to send OTP email")


# -------------------- STEP 1: Signup Request --------------------
@app.post("/signup-request")
async def signup_request(user: UserCreate):
    """User submits username, email, password — send OTP to email."""
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Store OTP temporarily in db.otp_verifications
    await db.otp_verifications.insert_one({
        "email": user.email,
        "username": user.username,
        "password": hash_password(user.password),
        "otp": otp,
        "verified": False,
    })

    # Send OTP via email
    send_otp_email(user.email, otp)

    return {"message": "OTP sent to your email for verification."}


# -------------------- STEP 2: Verify OTP --------------------
@app.post("/signup-verify")
async def signup_verify(data: dict):
    """User enters email + OTP to verify and create account."""
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        raise HTTPException(status_code=400, detail="Email and OTP required")

    otp_entry = await db.otp_verifications.find_one({"email": email})
    if not otp_entry:
        raise HTTPException(status_code=404, detail="No OTP request found for this email")

    if otp_entry["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Create actual user account
    new_user = {
        "username": otp_entry["username"],
        "email": otp_entry["email"],
        "password": otp_entry["password"],
    }
    await db.users.insert_one(new_user)

    # Mark OTP as used (optional: delete)
    await db.otp_verifications.delete_one({"email": email})

    return {"message": "Account verified successfully!"}


# -------------------- LOGIN --------------------
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await db.users.find_one({"username": form_data.username})
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        {"sub": db_user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}


# -------------------- PROFILE --------------------
@app.get("/me", response_model=UserOut)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return UserOut(username=current_user["username"], email=current_user["email"])
