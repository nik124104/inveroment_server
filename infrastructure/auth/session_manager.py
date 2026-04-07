"""
Управление сессиями пользователей
Хранение активных сессий, проверка, инвалидация
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
from infrastructure.database.connection_pool import database_service

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Менеджер сессий с хранением в БД
    Для 15 пользователей БД подойдёт, для больших нагрузок - Redis
    """
    
    def __init__(self):
        self.session_timeout_hours = 24  # Время жизни сессии
        
    async def create_session(self, user_id: int, token: str, ip_address: str = None, user_agent: str = None) -> bool:
        """
        Создание сессии в БД
        """
        try:
            expires_at = datetime.now() + timedelta(hours=self.session_timeout_hours)
            
            query = """
                INSERT INTO user_sessions (user_id, token, ip_address, user_agent, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            await database_service.execute(
                query, 
                (user_id, token, ip_address, user_agent, expires_at)
            )
            
            logger.info(f"Session created for user_id: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return False
    
    async def validate_session(self, token: str) -> Optional[Dict]:
        """
        Проверка активной сессии по токену
        """
        query = """
            SELECT 
                s.id,
                s.user_id,
                u.login,
                u.role,
                s.expires_at,
                s.created_at
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = %s AND s.expires_at > NOW()
        """
        
        session = await database_service.fetch_one(query, (token,))
        
        if session:
            # Обновляем время последнего использования (опционально)
            await self.update_last_activity(session['id'])
            
        return session
    
    async def update_last_activity(self, session_id: int):
        """
        Обновление времени последней активности
        """
        query = """
            UPDATE user_sessions 
            SET last_activity = NOW() 
            WHERE id = %s
        """
        await database_service.execute(query, (session_id,))
    
    async def invalidate_session(self, token: str) -> bool:
        """
        Инвалидация сессии (выход)
        """
        query = "DELETE FROM user_sessions WHERE token = %s"
        rows = await database_service.execute(query, (token,))
        
        if rows > 0:
            logger.info(f"Session invalidated: {token[:20]}...")
            return True
        return False
    
    async def invalidate_all_user_sessions(self, user_id: int) -> int:
        """
        Инвалидация всех сессий пользователя (при смене пароля)
        """
        query = "DELETE FROM user_sessions WHERE user_id = %s"
        rows = await database_service.execute(query, (user_id,))
        logger.info(f"Invalidated {rows} sessions for user_id: {user_id}")
        return rows
    
    async def get_active_sessions(self, user_id: int = None) -> List[Dict]:
        """
        Получение активных сессий
        """
        if user_id:
            query = """
                SELECT id, token, ip_address, user_agent, created_at, expires_at, last_activity
                FROM user_sessions
                WHERE user_id = %s AND expires_at > NOW()
                ORDER BY created_at DESC
            """
            return await database_service.fetch_all(query, (user_id,))
        else:
            query = """
                SELECT 
                    s.id, s.user_id, u.login, s.token, s.ip_address, 
                    s.created_at, s.expires_at, s.last_activity
                FROM user_sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.expires_at > NOW()
                ORDER BY s.created_at DESC
            """
            return await database_service.fetch_all(query)
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Очистка просроченных сессий
        """
        query = "DELETE FROM user_sessions WHERE expires_at < NOW()"
        rows = await database_service.execute(query)
        if rows > 0:
            logger.info(f"Cleaned up {rows} expired sessions")
        return rows

# Глобальный экземпляр
session_manager = SessionManager()