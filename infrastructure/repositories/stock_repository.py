"""
Репозиторий для работы с остатками
"""

from typing import List, Dict, Optional
from decimal import Decimal
from infrastructure.database.connection_pool import database_service

class StockRepository:
    """Репозиторий для работы с остатками"""
    
    def __init__(self, db=None):
        self.db = db or database_service
        
    async def get_all_with_details(self, only_positive: bool = False) -> List[Dict]:
        """Получить все остатки с деталями материалов"""
        query = """
            SELECT 
                m.id,
                m.name,
                m.article,
                m.min_stock,
                s.quantity,
                u.short_name as unit,
                CASE 
                    WHEN s.quantity = 0 THEN 'absent'
                    WHEN s.quantity < m.min_stock THEN 'low'
                    ELSE 'normal'
                END as status
            FROM materials m
            JOIN stock s ON s.material_id = m.id
            JOIN units u ON u.id = m.unit_id
        """
        
        if only_positive:
            query += " WHERE s.quantity > 0"
            
        query += " ORDER BY m.name"
        
        return await self.db.fetch_all(query)
    
    async def get_by_material_id(self, material_id: int) -> Optional[Dict]:
        """Получить остаток по ID материала"""
        query = """
            SELECT 
                m.id,
                m.name,
                m.article,
                m.min_stock,
                s.quantity,
                u.short_name as unit
            FROM materials m
            JOIN stock s ON s.material_id = m.id
            JOIN units u ON u.id = m.unit_id
            WHERE m.id = %s
        """
        return await self.db.fetch_one(query, (material_id,))
    
    async def get_low_stock(self) -> List[Dict]:
        """Получить материалы с остатком ниже минимума"""
        query = """
            SELECT 
                m.id,
                m.name,
                m.article,
                m.min_stock,
                s.quantity,
                u.short_name as unit,
                (m.min_stock - s.quantity) as deficit
            FROM materials m
            JOIN stock s ON s.material_id = m.id
            JOIN units u ON u.id = m.unit_id
            WHERE s.quantity < m.min_stock
            ORDER BY deficit DESC
        """
        return await self.db.fetch_all(query)