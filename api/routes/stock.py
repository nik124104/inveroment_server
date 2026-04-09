"""
Эндпоинты для работы с остатками и транзакциями
"""

from fastapi import APIRouter, HTTPException, Depends
from decimal import Decimal
from typing import List
import logging

from application.dto.schemas import (
    StockItemResponse, 
    TransactionRequest, 
    TransactionResponse
)
from infrastructure.repositories.stock_repository import StockRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Warehouse"])


@router.get(
    "/stock",
    response_model=List[StockItemResponse],
    summary="Остатки материалов",
    description="Возвращает список всех материалов с текущими остатками."
)
async def get_stock(
    only_positive: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Получить все остатки материалов (требует авторизации)"""
    repo = StockRepository()
    stock = await repo.get_all_with_details(only_positive)
    logger.info(f"User {current_user['login']} requested stock list")
    return stock


@router.get(
    "/stock/low",
    summary="Критический остаток",
    description="Возвращает материалы, у которых остаток ниже минимального."
)
async def get_low_stock(
    current_user: dict = Depends(get_current_user)
):
    """Получить материалы с остатком ниже минимума"""
    repo = StockRepository()
    low_stock = await repo.get_low_stock()
    logger.info(f"User {current_user['login']} requested low stock list")
    return low_stock


@router.get(
    "/stock/{material_id}",
    summary="Остаток материала",
    description="Возвращает остаток конкретного материала по его ID."
)
async def get_stock_by_material(
    material_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Получить остаток конкретного материала"""
    repo = StockRepository()
    stock = await repo.get_by_material_id(material_id)
    if not stock:
        raise HTTPException(404, f"Material {material_id} not found")
    return stock


@router.post(
    "/material/in",
    summary="Приход материала",
    description="Оприходование материала на склад. Увеличивает остаток."
)
async def material_in(
    request: TransactionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Приход материала"""
    try:
        repo = TransactionRepository()
        trans_id = await repo.create(
            trans_type='IN',
            user_id=current_user['id'],
            material_id=request.material_id,
            quantity=request.quantity,
            comment=request.comment
        )
        logger.info(f"Material IN: user={current_user['login']}, material={request.material_id}, qty={request.quantity}")
        return {
            "status": "success",
            "transaction_id": trans_id,
            "message": f"Приход {request.quantity} единиц выполнен"
        }
    except Exception as e:
        logger.error(f"Error in material_in: {e}")
        raise HTTPException(500, str(e))


@router.post(
    "/material/out",
    summary="Расход материала",
    description="Списание материала со склада. Проверяет наличие достаточного остатка."
)
async def material_out(
    request: TransactionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Расход материала с проверкой остатка"""
    try:
        stock_repo = StockRepository()
        current_stock = await stock_repo.get_by_material_id(request.material_id)
        
        if not current_stock:
            raise HTTPException(404, f"Material {request.material_id} not found")
        
        if current_stock['quantity'] < request.quantity:
            raise HTTPException(
                400, 
                f"Недостаточно материала. Доступно: {current_stock['quantity']}, запрошено: {request.quantity}"
            )
        
        repo = TransactionRepository()
        trans_id = await repo.create(
            trans_type='OUT',
            user_id=current_user['id'],
            material_id=request.material_id,
            quantity=request.quantity,
            comment=request.comment
        )
        logger.info(f"Material OUT: user={current_user['login']}, material={request.material_id}, qty={request.quantity}")
        return {
            "status": "success",
            "transaction_id": trans_id,
            "message": f"Расход {request.quantity} единиц выполнен"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in material_out: {e}")
        raise HTTPException(500, str(e))


@router.get(
    "/transactions",
    summary="История операций",
    description="Возвращает список всех операций (приходов и расходов) с пагинацией."
)
async def get_transactions(
    limit: int = 100, 
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Получить историю операций"""
    repo = TransactionRepository()
    transactions = await repo.get_all(limit, offset)
    logger.info(f"User {current_user['login']} requested transactions history")
    return transactions


@router.get(
    "/transactions/material/{material_id}",
    summary="Движения материала",
    description="Возвращает историю операций по конкретному материалу."
)
async def get_material_transactions(
    material_id: int, 
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Получить движения по конкретному материалу"""
    repo = TransactionRepository()
    movements = await repo.get_by_material(material_id, limit)
    return movements


@router.get(
    "/stats/today",
    summary="Статистика за сегодня",
    description="Возвращает количество и сумму приходов/расходов за текущий день."
)
async def get_today_stats(
    current_user: dict = Depends(get_current_user)
):
    """Получить статистику за сегодня"""
    repo = TransactionRepository()
    stats = await repo.get_today_stats()
    return stats