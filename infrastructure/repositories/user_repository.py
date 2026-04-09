"""
Репозиторий для работы с пользователями (реализация MySQL)
"""

from typing import Optional, Dict, List
from domain.repositories.user_repository import UserRepositoryInterface
from infrastructure.database.connection_pool import database_service


class UserRepository(UserRepositoryInterface):
    """Реализация UserRepository для MySQL"""
    
    def __init__(self, db=None):
        self.db = db or database_service
    
    async def get_by_login(self, login: str) -> Optional[Dict]:
        """Получить пользователя по логину"""
        query = """
            SELECT id, login, full_name, password_hash, role, is_active, created_at
            FROM users
            WHERE login = %s
        """
        return await self.db.fetch_one(query, (login,))
    
    async def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        query = """
            SELECT id, login, full_name, role, is_active, created_at, last_login
            FROM users
            WHERE id = %s
        """
        return await self.db.fetch_one(query, (user_id,))
    
    async def get_all(self) -> List[Dict]:
        """Получить всех пользователей"""
        query = """
            SELECT id, login, full_name, role, is_active, created_at, last_login
            FROM users
            ORDER BY id
        """
        return await self.db.fetch_all(query)
    
    async def update_last_login(self, user_id: int) -> bool:
        """Обновить время последнего входа"""
        query = "UPDATE users SET last_login = NOW() WHERE id = %s"
        rows = await self.db.execute(query, (user_id,))
        return rows > 0
    
    async def change_password(self, user_id: int, new_password_hash: str) -> bool:
        """Смена пароля"""
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        rows = await self.db.execute(query, (new_password_hash, user_id))
        return rows > 0

# Глобальный экземпляр
user_repository = UserRepository()