import asyncio
import logging
from fastapi import FastAPI
import uvicorn
from api.routes import auth, stock, health, material_groups
from config import config
from infrastructure.database.connection_pool import database_service
from api.routes import health

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаём FastAPI приложение
app = FastAPI(
    title="Warehouse Inventory API",
    description="API для учёта материалов в отделе",
    version="1.0.0"
)

# Регистрируем роуты
app.include_router(health.router, prefix="", tags=["System"])
app.include_router(auth.router)
app.include_router(stock.router)
app.include_router(material_groups.router)

class WarehouseServer:
    """Главный класс сервера"""
    
    def __init__(self):
        self.is_running = False
        
    async def start(self):
        """Запуск сервера"""
        logger.info("🚀 Starting Warehouse Server...")
        
        # Запускаем сервис БД
        await database_service.start()
        
        self.is_running = True
        logger.info(f"✅ Server started on http://{config.server.host}:{config.server.port}")
        logger.info(f"📖 API docs: http://{config.server.host}:{config.server.port}/docs")
        
    async def stop(self):
        """Остановка сервера"""
        logger.info("🛑 Stopping Warehouse Server...")
        self.is_running = False
        await database_service.stop()
        logger.info("✅ Server stopped")

async def main():
    """Точка входа"""
    server = WarehouseServer()
    await server.start()
    
    # Запускаем FastAPI сервер
    config_uv = uvicorn.Config(
        app=app,
        host=config.server.host,
        port=config.server.port,
        log_level="info"
    )
    server_uv = uvicorn.Server(config_uv)
    await server_uv.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")