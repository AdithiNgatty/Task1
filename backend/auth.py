from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import random

from backend.database import db
from backend.email_utils import send_otp_email

# ---------------- Password Hashing ----------------
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ---------------- JWT Setup ----------------
SECRET_KEY = "mysecretkey"  # ⚠️ move to .env file in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ---------------- OAuth2 Scheme ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---------------- Collections ----------------
users = db["users"]
pending_users = db["pending_users"]

# ---------------- Router ----------------
router = APIRouter()


# ======================================================
# 🧩 STEP 1 — SIGNUP REQUEST (SEND OTP TO EMAIL)
# ======================================================
@router.post("/signup-request")
async def signup_request(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    # Check if user already exists
    existing_user = await users.find_one({"$or": [{"email": email}, {"username": username}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists with this email or username.")

    # Generate OTP and expiry
    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=5)

    # Store temporarily
    await pending_users.insert_one({
        "username": username,
        "email": email,
        "password": hash_password(password),
        "otp": otp,
        "otp_expiry": expiry
    })

    # Send OTP via email
    send_otp_email(email, otp)

    return {"message": "OTP sent to your email. Please verify to complete signup."}


# ======================================================
# 🧩 STEP 2 — OTP VERIFICATION (CREATE ACCOUNT)
# ======================================================
@router.post("/signup-verify")
async def signup_verify(email: str = Form(...), otp: str = Form(...)):
    pending_user = await pending_users.find_one({"email": email})

    if not pending_user:
        raise HTTPException(status_code=404, detail="No pending signup found for this email.")
    if datetime.utcnow() > pending_user["otp_expiry"]:
        await pending_users.delete_one({"_id": pending_user["_id"]})
        raise HTTPException(status_code=400, detail="OTP expired. Please sign up again.")
    if otp != pending_user["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    # Create verified user
    await users.insert_one({
        "username": pending_user["username"],
        "email": pending_user["email"],
        "password": pending_user["password"],
    })
    await pending_users.delete_one({"_id": pending_user["_id"]})

    return {"message": "Account verified and created successfully!"}


# ======================================================
# 🔐 LOGIN (JWT TOKEN GENERATION)
# ======================================================
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate access token
    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# ======================================================
# 👤 GET CURRENT USER (TOKEN VALIDATION)
# ======================================================
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decode JWT, extract username, and return user from MongoDB.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await users.find_one({"username": username})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ======================================================
#  PROFILE ENDPOINT (PROTECTED ROUTE)
# ======================================================
@router.get("/me")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Returns profile details for the currently authenticated user.
    """
    return {
        "username": current_user["username"],
        "email": current_user["email"],
    }
