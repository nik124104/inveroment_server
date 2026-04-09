"""
Интерфейс репозитория для работы с транзакциями
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from decimal import Decimal


class TransactionRepositoryInterface(ABC):
    """Интерфейс репозитория транзакций"""
    
    @abstractmethod
    async def create(self, trans_type: str, user_id: int, 
                     material_id: int, quantity: Decimal, 
                     comment: str = "") -> int:
        """Создать транзакцию"""
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Получить все транзакции"""
        pass
    
    @abstractmethod
    async def get_by_material(self, material_id: int, limit: int = 50) -> List[Dict]:
        """Получить движения по материалу"""
        pass
    
    @abstractmethod
    async def get_today_stats(self) -> Dict:
        """Получить статистику за сегодня"""
        pass