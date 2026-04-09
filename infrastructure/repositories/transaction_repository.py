"""
Репозиторий для работы с транзакциями (реализация MySQL)
"""

from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime
from domain.repositories.transaction_repository import TransactionRepositoryInterface
from infrastructure.database.connection_pool import database_service


class TransactionRepository(TransactionRepositoryInterface):
    """Реализация TransactionRepository для MySQL"""
    
    def __init__(self, db=None):
        self.db = db or database_service
    
    async def create(self, trans_type: str, user_id: int, 
                     material_id: int, quantity: Decimal, 
                     comment: str = "") -> int:
        """Создать транзакцию"""
        async with self.db.transaction() as conn:
            query_trans = """
                INSERT INTO transactions (type, user_id, comment)
                VALUES (%s, %s, %s)
            """
            async with conn.cursor() as cur:
                await cur.execute(query_trans, (trans_type, user_id, comment))
                trans_id = cur.lastrowid
                
                query_item = """
                    INSERT INTO transaction_items (transaction_id, material_id, quantity)
                    VALUES (%s, %s, %s)
                """
                await cur.execute(query_item, (trans_id, material_id, quantity))
                
                return trans_id
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Получить все транзакции"""
        query = """
            SELECT 
                t.id,
                t.type,
                t.created_at,
                u.login as user_name,
                t.comment,
                COUNT(ti.id) as items_count,
                SUM(ti.quantity) as total_quantity
            FROM transactions t
            JOIN users u ON u.id = t.user_id
            JOIN transaction_items ti ON ti.transaction_id = t.id
            GROUP BY t.id
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s
        """
        return await self.db.fetch_all(query, (limit, offset))
    
    async def get_by_material(self, material_id: int, limit: int = 50) -> List[Dict]:
        """Получить движения по материалу"""
        query = """
            SELECT 
                t.id,
                t.type,
                t.created_at,
                u.login as user_name,
                ti.quantity,
                t.comment
            FROM transactions t
            JOIN transaction_items ti ON ti.transaction_id = t.id
            JOIN users u ON u.id = t.user_id
            WHERE ti.material_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s
        """
        return await self.db.fetch_all(query, (material_id, limit))
    
    async def get_today_stats(self) -> Dict:
        """Получить статистику за сегодня"""
        query = """
            SELECT 
                COUNT(DISTINCT CASE WHEN type = 'IN' THEN t.id END) as in_count,
                COUNT(DISTINCT CASE WHEN type = 'OUT' THEN t.id END) as out_count,
                COALESCE(SUM(CASE WHEN type = 'IN' THEN ti.quantity ELSE 0 END), 0) as in_quantity,
                COALESCE(SUM(CASE WHEN type = 'OUT' THEN ti.quantity ELSE 0 END), 0) as out_quantity
            FROM transactions t
            JOIN transaction_items ti ON ti.transaction_id = t.id
            WHERE DATE(t.created_at) = CURDATE()
        """
        result = await self.db.fetch_one(query)
        return result or {}