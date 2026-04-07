"""
Middleware для проверки JWT токена
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from infrastructure.auth.jwt_handler import jwt_handler

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Получение текущего пользователя из JWT токена
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Проверяем JWT токен
    payload = jwt_handler.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": payload['user_id'],
        "login": payload['login'],
        "role": payload['role'],
        "full_name": payload.get('full_name')
    }


async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Только администратор"""
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin rights required"
        )
    return current_user