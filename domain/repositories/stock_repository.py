"""
Интерфейс репозитория для работы с остатками
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from decimal import Decimal


class StockRepositoryInterface(ABC):
    """Интерфейс репозитория остатков"""
    
    @abstractmethod
    async def get_all_with_details(self, only_positive: bool = False) -> List[Dict]:
        """Получить все остатки с деталями материалов"""
        pass
    
    @abstractmethod
    async def get_by_material_id(self, material_id: int) -> Optional[Dict]:
        """Получить остаток по ID материала"""
        pass
    
    @abstractmethod
    async def get_low_stock(self) -> List[Dict]:
        """Получить материалы с остатком ниже минимума"""
        pass