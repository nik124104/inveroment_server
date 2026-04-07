"""
Хеширование и проверка паролей
"""

import hashlib

class PasswordHasher:
    """Хеширование паролей (SHA-256)"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Хеширование пароля
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Проверка пароля
        """
        computed_hash = PasswordHasher.hash_password(password)
        return computed_hash == password_hash

# Глобальный экземпляр
password_hasher = PasswordHasher()