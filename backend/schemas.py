from pydantic import BaseModel, validator
import re
from typing import List

class UserCreate(BaseModel):
    login: str
    password: str

    @validator('login')
    def validate_login(cls, v):
        if len(v) < 3 or len(v) > 32:
            raise ValueError('Login must be between 3 and 32 characters')
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Login can only contain letters, numbers, ., _, -')
        return v

    @validator('password')
    def validate_password(cls, v):
        errors = []
        if len(v) < 8:
            errors.append('Must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            errors.append('Must contain at least one uppercase letter (A-Z)')
        if not re.search(r'[a-z]', v):
            errors.append('Must contain at least one lowercase letter (a-z)')
        if not re.search(r'[0-9]', v):
            errors.append('Must contain at least one digit (0-9)')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append('Must contain at least one special character (!@#$%^&* etc.)')
        
        if errors:
            # Простой формат без переносов строк
            error_message = "; ".join(errors)
            raise ValueError(error_message)
        return v

class UserResponse(BaseModel):
    message: str
    user_id: int = None

class LoginRequest(BaseModel):
    login: str
    password: str