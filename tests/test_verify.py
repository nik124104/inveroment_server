import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

# Тест
stored = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
password = "admin123"

print(f"Password: {password}")
print(f"Stored: {stored}")
print(f"Computed: {hash_password(password)}")
print(f"Match: {verify_password(password, stored)}")

# Проверка на баги с кодировкой
print(f"\nCheck encoding:")
print(f"Bytes: {password.encode('utf-8')}")
print(f"Hex: {hashlib.sha256(password.encode('utf-8')).hexdigest()}")