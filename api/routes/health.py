from fastapi import APIRouter
from infrastructure.database.connection_pool import database_service

router = APIRouter()

@router.get("/health")
async def health_check():
    """Проверка работоспособности сервера"""
    return {"status": "ok", "message": "Warehouse server is running"}

@router.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "name": "Warehouse Inventory System",
        "version": "1.0.0",
        "status": "running"
    }

@router.get("/db-test")
async def test_database():
    """Тест подключения к БД"""
    try:
        result = await database_service.fetch_one("SELECT 1 as test, NOW() as time")
        return {
            "status": "connected",
            "test": result,
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }