# domain/repositories/__init__.py
from .stock_repository import StockRepositoryInterface
from .transaction_repository import TransactionRepositoryInterface
from .user_repository import UserRepositoryInterface
from .material_group_repository import MaterialGroupRepositoryInterface

__all__ = [
    'StockRepositoryInterface',
    'TransactionRepositoryInterface',
    'UserRepositoryInterface',
    'MaterialGroupRepositoryInterface'
]