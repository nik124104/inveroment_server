"""
Репозиторий для работы с пользователями
"""

from typing import Optional, Dict, List
from infrastructure.database.connection_pool import database_service

class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    async def get_by_login(self, login: str) -> Optional[Dict]:
        """Получить пользователя по логину"""
        import logging
        logger = logging.getLogger(__name__)
    
        logger.info(f"=== REPOSITORY: Looking for user: {login}")
    
        query = """
            SELECT id, login, full_name, password_hash, role, is_active, created_at
            FROM users
            WHERE login = %s
        """
        result = await database_service.fetch_one(query, (login,))
    
        logger.info(f"=== REPOSITORY: Result found: {result is not None}")
        if result:
            logger.info(f"=== REPOSITORY: User id: {result.get('id')}, hash: {result.get('password_hash')[:20]}...")
    
        return result
    
    async def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        query = """
            SELECT id, login, full_name, role, is_active, created_at, last_login
            FROM users
            WHERE id = %s
        """
        return await database_service.fetch_one(query, (user_id,))
    
    async def get_all(self) -> List[Dict]:
        """Получить всех пользователей"""
        query = """
            SELECT id, login, full_name, role, is_active, created_at, last_login
            FROM users
            ORDER BY id
        """
        return await database_service.fetch_all(query)
    
    async def update_last_login(self, user_id: int) -> bool:
        """Обновить время последнего входа"""
        query = "UPDATE users SET last_login = NOW() WHERE id = %s"
        rows = await database_service.execute(query, (user_id,))
        return rows > 0
    
    async def change_password(self, user_id: int, new_password_hash: str) -> bool:
        """Смена пароля"""
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        rows = await database_service.execute(query, (new_password_hash, user_id))
        return rows > 0

# Глобальный экземпляр
user_repository = UserRepository()