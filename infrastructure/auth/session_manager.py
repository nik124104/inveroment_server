"""
Управление сессиями пользователей (только в памяти)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Менеджер сессий (хранение в памяти)
    Для 15 пользователей этого достаточно
    """
    
    def __init__(self):
        self.session_timeout_hours = 24
        # Хранилище сессий: session_id -> данные
        self._sessions: Dict[int, Dict] = {}
        self._next_id = 1
        # Маппинг токен -> session_id для быстрого поиска
        self._token_to_session: Dict[str, int] = {}
        
    def create_session(self, user_id: int, token: str, login: str, role: str, 
                       full_name: str = None, ip_address: str = None, user_agent: str = None) -> int:
        """
        Создание сессии в памяти
        Возвращает ID сессии
        """
        try:
            expires_at = datetime.now() + timedelta(hours=self.session_timeout_hours)
            session_id = self._next_id
            self._next_id += 1
            
            session = {
                'id': session_id,
                'user_id': user_id,
                'token': token,
                'login': login,
                'role': role,
                'full_name': full_name,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'created_at': datetime.now(),
                'expires_at': expires_at,
                'last_activity': datetime.now()
            }
            
            self._sessions[session_id] = session
            self._token_to_session[token] = session_id
            
            logger.info(f"Session created for user: {login}, session_id: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return -1
    
    def validate_session(self, token: str) -> Optional[Dict]:
        """
        Проверка активной сессии по токену
        """
        session_id = self._token_to_session.get(token)
        if not session_id:
            logger.warning(f"Session not found for token: {token[:20]}...")
            return None
        
        session = self._sessions.get(session_id)
        if not session:
            # Очищаем невалидную ссылку
            del self._token_to_session[token]
            return None
        
        # Проверяем срок действия
        if session['expires_at'] < datetime.now():
            # Удаляем просроченную сессию
            self._invalidate_by_id(session_id)
            logger.warning(f"Session expired: {token[:20]}...")
            return None
        
        # Обновляем время активности
        session['last_activity'] = datetime.now()
        
        return {
            'id': session['user_id'],
            'user_id': session['user_id'],
            'login': session['login'],
            'role': session['role'],
            'full_name': session.get('full_name'),
            'session_id': session_id
        }
    
    def invalidate_session(self, token: str) -> bool:
        """
        Инвалидация сессии (выход)
        """
        session_id = self._token_to_session.get(token)
        if session_id:
            self._invalidate_by_id(session_id)
            return True
        return False
    
    def invalidate_session_by_id(self, session_id: int) -> bool:
        """
        Инвалидация сессии по ID
        """
        session = self._sessions.get(session_id)
        if session:
            token = session['token']
            del self._token_to_session[token]
            del self._sessions[session_id]
            logger.info(f"Session invalidated by id: {session_id}")
            return True
        return False
    
    def _invalidate_by_id(self, session_id: int):
        """Внутренний метод инвалидации по ID"""
        session = self._sessions.get(session_id)
        if session:
            token = session['token']
            if token in self._token_to_session:
                del self._token_to_session[token]
            del self._sessions[session_id]
            logger.info(f"Session invalidated: {session_id}")
    
    def invalidate_all_user_sessions(self, user_id: int) -> int:
        """
        Инвалидация всех сессий пользователя (при смене пароля)
        """
        sessions_to_remove = []
        for session_id, session in self._sessions.items():
            if session['user_id'] == user_id:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self._invalidate_by_id(session_id)
        
        logger.info(f"Invalidated {len(sessions_to_remove)} sessions for user_id: {user_id}")
        return len(sessions_to_remove)
    
    def get_active_sessions(self, user_id: int = None) -> List[Dict]:
        """
        Получение активных сессий
        """
        now = datetime.now()
        result = []
        
        for session_id, session in self._sessions.items():
            # Пропускаем просроченные
            if session['expires_at'] < now:
                continue
            
            if user_id is None or session['user_id'] == user_id:
                result.append({
                    'id': session_id,
                    'token': session['token'],  # для внутреннего использования
                    'user_id': session['user_id'],
                    'login': session['login'],
                    'ip_address': session.get('ip_address'),
                    'user_agent': session.get('user_agent', '').split('(')[0].strip() if session.get('user_agent') else None,
                    'created_at': session['created_at'],
                    'expires_at': session['expires_at'],
                    'last_activity': session['last_activity']
                })
        
        return result
    
    def cleanup_expired_sessions(self) -> int:
        """
        Очистка просроченных сессий
        """
        now = datetime.now()
        sessions_to_remove = [
            session_id for session_id, session in self._sessions.items()
            if session['expires_at'] < now
        ]
        
        for session_id in sessions_to_remove:
            self._invalidate_by_id(session_id)
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} expired sessions")
        
        return len(sessions_to_remove)
    
    def get_session_count(self) -> int:
        """Количество активных сессий"""
        self.cleanup_expired_sessions()
        return len(self._sessions)


# Глобальный экземпляр
session_manager = SessionManager()