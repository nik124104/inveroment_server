"""
Репозиторий для работы с группами материалов (реализация MySQL)
"""

from typing import Optional, List, Dict
import logging
from domain.repositories.material_group_repository import MaterialGroupRepositoryInterface
from infrastructure.database.connection_pool import database_service

logger = logging.getLogger(__name__)


class MaterialGroupRepository(MaterialGroupRepositoryInterface):
    """Реализация MaterialGroupRepository для MySQL"""
    
    def __init__(self, db=None):
        self.db = db or database_service
    
    async def create(self, name: str, parent_id: Optional[int] = None) -> int:
        """Создание группы"""
        query = """
            INSERT INTO material_groups (name, parent_id)
            VALUES (%s, %s)
        """
        await self.db.execute(query, (name, parent_id))
        
        result = await self.db.fetch_one("SELECT LAST_INSERT_ID() as id")
        group_id = result['id'] if result else 0
        
        logger.info(f"Material group created: id={group_id}, name={name}")
        return group_id
    
    async def get_by_id(self, group_id: int) -> Optional[Dict]:
        """Получение группы по ID"""
        query = """
            SELECT 
                g.id,
                g.name,
                g.parent_id,
                p.name as parent_name,
                (SELECT COUNT(*) FROM material_groups WHERE parent_id = g.id) as children_count
            FROM material_groups g
            LEFT JOIN material_groups p ON p.id = g.parent_id
            WHERE g.id = %s
        """
        return await self.db.fetch_one(query, (group_id,))
    
    async def get_all(self, include_children_count: bool = True) -> List[Dict]:
        """Получение всех групп"""
        if include_children_count:
            query = """
                SELECT 
                    g.id,
                    g.name,
                    g.parent_id,
                    p.name as parent_name,
                    (SELECT COUNT(*) FROM material_groups WHERE parent_id = g.id) as children_count
                FROM material_groups g
                LEFT JOIN material_groups p ON p.id = g.parent_id
                ORDER BY g.id
            """
        else:
            query = """
                SELECT id, name, parent_id
                FROM material_groups
                ORDER BY id
            """
        
        return await self.db.fetch_all(query)
    
    async def get_tree(self) -> List[Dict]:
        """Получение древовидной структуры"""
        all_groups = await self.get_all(include_children_count=False)
        
        groups_by_id = {}
        for g in all_groups:
            groups_by_id[g['id']] = {
                'id': g['id'],
                'name': g['name'],
                'parent_id': g['parent_id'],
                'children': [],
                'level': 0
            }
        
        tree = []
        for group in all_groups:
            if group['parent_id'] is None:
                tree.append(groups_by_id[group['id']])
            else:
                parent = groups_by_id.get(group['parent_id'])
                if parent:
                    parent['children'].append(groups_by_id[group['id']])
        
        def set_level(node, level=0):
            node['level'] = level
            for child in node['children']:
                set_level(child, level + 1)
        
        for node in tree:
            set_level(node)
        
        return tree
    
    async def get_children(self, parent_id: int) -> List[Dict]:
        """Получение дочерних групп"""
        query = """
            SELECT id, name, parent_id
            FROM material_groups
            WHERE parent_id = %s
            ORDER BY name
        """
        return await self.db.fetch_all(query, (parent_id,))
    
    async def update(self, group_id: int, name: str = None, parent_id: int = None) -> bool:
        """Обновление группы"""
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        
        if parent_id is not None:
            if parent_id == group_id:
                raise ValueError("Cannot set group as its own parent")
            updates.append("parent_id = %s")
            params.append(parent_id)
        
        if not updates:
            return True
        
        query = f"UPDATE material_groups SET {', '.join(updates)} WHERE id = %s"
        params.append(group_id)
        
        rows = await self.db.execute(query, tuple(params))
        logger.info(f"Material group updated: id={group_id}")
        return rows > 0
    
    async def delete(self, group_id: int) -> bool:
        """Удаление группы"""
        if await self.has_children(group_id):
            raise ValueError("Cannot delete group with children")
        
        if await self.has_materials(group_id):
            raise ValueError("Cannot delete group that has materials")
        
        query = "DELETE FROM material_groups WHERE id = %s"
        rows = await self.db.execute(query, (group_id,))
        
        if rows > 0:
            logger.info(f"Material group deleted: id={group_id}")
        return rows > 0
    
    async def has_children(self, group_id: int) -> bool:
        """Проверка наличия дочерних групп"""
        query = "SELECT COUNT(*) as count FROM material_groups WHERE parent_id = %s"
        result = await self.db.fetch_one(query, (group_id,))
        return result['count'] > 0 if result else False
    
    async def has_materials(self, group_id: int) -> bool:
        """Проверка наличия материалов в группе"""
        query = "SELECT COUNT(*) as count FROM materials WHERE group_id = %s"
        result = await self.db.fetch_one(query, (group_id,))
        return result['count'] > 0 if result else False
    
    async def get_path(self, group_id: int) -> List[Dict]:
        """Получение пути от корня до группы"""
        # Для простоты возвращаем только саму группу
        group = await self.get_by_id(group_id)
        return [{'id': group['id'], 'name': group['name']}] if group else []


# Глобальный экземпляр
material_group_repository = MaterialGroupRepository()