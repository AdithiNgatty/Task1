from pydantic import BaseModel, EmailStr

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
