from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import random, smtplib, os
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

from backend.database import db
from backend.models import UserCreate, OTPVerify, UserOut
from backend.auth import hash_password, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

# -------------------- Load .env explicitly --------------------
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    raise RuntimeError(f".env file not found at {env_path}")

load_dotenv(dotenv_path=env_path)

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# -------------------- Debug check --------------------
if not SENDER_EMAIL or not SENDER_PASSWORD:
    raise RuntimeError("SENDER_EMAIL or SENDER_PASSWORD not set in .env")

print("SENDER_EMAIL loaded:", SENDER_EMAIL)

# -------------------- FastAPI app --------------------
app = FastAPI(title="FastAPI Auth with MongoDB + OTP")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Helper: Send OTP --------------------
def send_otp_email(recipient_email: str, otp: str):
    try:
        msg = MIMEText(f"Your OTP code is: {otp}\nIt will expire in 5 minutes.")
        msg["Subject"] = "Your OTP Verification Code"
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"OTP sent to {recipient_email}: {otp}")

    except Exception as e:
        print("Email sending failed:", e)
        raise HTTPException(status_code=500, detail="Failed to send OTP email")


# -------------------- Signup request (send OTP) --------------------
@app.post("/signup-request")
async def signup_request(user: UserCreate):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    otp = str(random.randint(100000, 999999))
    await db.otp_verifications.insert_one({
        "email": user.email,
        "username": user.username,
        "password": hash_password(user.password),
        "otp": otp,
        "verified": False,
    })

    send_otp_email(user.email, otp)
    return {"message": "OTP sent to your email for verification."}


# -------------------- Verify OTP --------------------
@app.post("/signup-verify")
async def signup_verify(data: OTPVerify):
    otp_entry = await db.otp_verifications.find_one({"email": data.email})
    if not otp_entry:
        raise HTTPException(status_code=404, detail="No OTP request found for this email")
    if otp_entry["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    new_user = {
        "username": otp_entry["username"],
        "email": otp_entry["email"],
        "password": otp_entry["password"],
    }
    await db.users.insert_one(new_user)
    await db.otp_verifications.delete_one({"email": data.email})

    return {"message": "Account verified successfully!"}


# -------------------- Login --------------------
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await db.users.find_one({"username": form_data.username})
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": db_user["username"]}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}


# -------------------- Protected profile route --------------------
@app.get("/me", response_model=UserOut)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return UserOut(username=current_user["username"], email=current_user["email"])
