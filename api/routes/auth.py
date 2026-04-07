"""
Эндпоинты для авторизации
"""

from fastapi import APIRouter, HTTPException, status, Depends
import logging
import sys
print("=== AUTH ROUTES LOADED ===", file=sys.stderr)

from application.dto.user_dto import LoginRequest, LoginResponse, UserInfo
from infrastructure.auth.password_hasher import password_hasher
from infrastructure.auth.jwt_handler import jwt_handler
from infrastructure.repositories.user_repository import user_repository
from api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    # ОТЛАДКА САМАЯ ПЕРВАЯ
    logger.info(f"=== START LOGIN ATTEMPT ===")
    logger.info(f"Login data received: {login_data.login}")
    
    # 1. Ищем пользователя в БД
    user = await user_repository.get_by_login(login_data.login)
    
    logger.info(f"User found: {user is not None}")
    
    if not user:
        logger.warning(f"Login failed: user {login_data.login} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password"
        )
    
    # ОТЛАДКА: выводим хеши для сравнения
    computed_hash = password_hasher.hash_password(login_data.password)
    logger.info(f"Login attempt: {login_data.login}")
    logger.info(f"Stored hash: {user['password_hash']}")
    logger.info(f"Computed hash: {computed_hash}")
    logger.info(f"Hash match: {computed_hash == user['password_hash']}")
    
    # 2. Проверяем пароль
    if not password_hasher.verify_password(login_data.password, user['password_hash']):
        logger.warning(f"Login failed: wrong password for {login_data.login}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password"
        )
    
    # 3. Проверяем активен ли пользователь
    if not user.get('is_active', True):
        logger.warning(f"Login failed: user {login_data.login} is disabled")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # 4. Создаём JWT токен
    token = jwt_handler.create_token(
        user_id=user['id'],
        login=user['login'],
        role=user['role'],
        full_name=user.get('full_name')
    )
    
    # 5. Обновляем время последнего входа
    await user_repository.update_last_login(user['id'])
    
    logger.info(f"User {login_data.login} logged in successfully")
    
    return LoginResponse(
        token=token,
        user_id=user['id'],
        login=user['login'],
        role=user['role'],
        full_name=user.get('full_name')
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Получить информацию о текущем пользователе (из токена)
    """
    return UserInfo(
        id=current_user['id'],
        login=current_user['login'],
        role=current_user['role'],
        full_name=current_user.get('full_name')
    )