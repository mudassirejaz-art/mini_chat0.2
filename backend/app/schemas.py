from pydantic import BaseModel, EmailStr, constr

class SignupRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class SignupResponse(BaseModel):
    status: str
    message: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class LoginResponse(BaseModel):
    status: str
    message: str
    access_token: str = None
    refresh_token: str = None
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    status: str
    access_token: str
    token_type: str = "bearer"
