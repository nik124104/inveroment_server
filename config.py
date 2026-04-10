"""
Конфигурация сервера
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем переменные из .env файла (создадим позже)
load_dotenv()

@dataclass
class DatabaseConfig:
    """Конфигурация подключения к БД"""
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = "root"
    database: str = "inventory"
    pool_size: int = 10
    pool_recycle: int = 3600
    
    def __post_init__(self):
        # Загружаем из переменных окружения
        self.host = os.getenv('DB_HOST', self.host)
        self.port = int(os.getenv('DB_PORT', self.port))
        self.user = os.getenv('DB_USER', self.user)
        self.password = os.getenv('DB_PASSWORD', self.password)
        self.database = os.getenv('DB_NAME', self.database)

@dataclass
class ServerConfig:
    """Конфигурация сервера"""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    secret_key: str = "your-super-secret-key-change-in-production"
    jwt_expire_hours: int = 24
    
    def __post_init__(self):
        self.host = os.getenv('SERVER_HOST', self.host)
        self.port = int(os.getenv('SERVER_PORT', self.port))
        self.secret_key = os.getenv('SECRET_KEY', self.secret_key)

@dataclass
class Config:
    """Главный конфиг"""
    db: DatabaseConfig = None
    server: ServerConfig = None
    
    def __init__(self):
        self.db = DatabaseConfig()
        self.server = ServerConfig()

# Создаём глобальный экземпляр конфига
config = Config()