"""
JWT токены: создание и валидация (без хранения в БД)
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging
from config import config

logger = logging.getLogger(__name__)

class JWTHandler:
    """Хендлер для работы с JWT токенами"""
    
    def __init__(self):
        self.secret_key = config.server.secret_key
        self.algorithm = "HS256"
        self.expire_hours = config.server.jwt_expire_hours
        
    def create_token(self, user_id: int, login: str, role: str, full_name: str = None) -> str:
        """
        Создание JWT токена (вся информация внутри токена)
        """
        payload = {
            'user_id': user_id,
            'login': login,
            'role': role,
            'full_name': full_name,
            'exp': datetime.utcnow() + timedelta(hours=self.expire_hours),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Token created for user: {login}")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Проверка и декодирование токена (без обращения к БД)
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

jwt_handler = JWTHandler()