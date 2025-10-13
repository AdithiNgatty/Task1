from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# -------------------- User models --------------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    email: EmailStr

# -------------------- OTP verification model --------------------
class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class BioIn(BaseModel):
    bio: str = Field(..., min_length=1, max_length=1000, description="User biography text")

class BioOut(BaseModel):
    username: str
    email: str
    bio: Optional[str] = None