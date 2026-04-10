"""
DTO для пользователей
"""

from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Запрос на логин"""
    login: str
    password: str

class LoginResponse(BaseModel):
    """Ответ на логин"""
    token: str
    user_id: int
    login: str
    role: str
    full_name: Optional[str] = None

class UserInfo(BaseModel):
    """Информация о пользователе"""
    id: int
    login: str
    role: str
    full_name: Optional[str] = None
    
class ChangePasswordRequest(BaseModel):
    """Запрос на смену пароля"""   
    login: str
    new_password: str