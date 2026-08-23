from pydantic import BaseModel, EmailStr

class CustomerCreate(BaseModel):
    email: EmailStr
    preferred_language: str = "en"
