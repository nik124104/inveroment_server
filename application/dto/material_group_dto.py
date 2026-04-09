"""
DTO для групп материалов
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MaterialGroupCreate(BaseModel):
    """Создание группы материалов"""
    name: str = Field(..., min_length=1, max_length=255, description="Название группы")
    parent_id: Optional[int] = Field(None, description="ID родительской группы")


class MaterialGroupUpdate(BaseModel):
    """Обновление группы материалов"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название группы")
    parent_id: Optional[int] = Field(None, description="ID родительской группы")


class MaterialGroupResponse(BaseModel):
    """Ответ с данными группы материалов"""
    id: int
    name: str
    parent_id: Optional[int] = None
    parent_name: Optional[str] = None
    children_count: int = 0
    created_at: Optional[datetime] = None


class MaterialGroupTreeResponse(BaseModel):
    """Древовидная структура групп"""
    id: int
    name: str
    parent_id: Optional[int] = None
    children: List['MaterialGroupTreeResponse'] = []
    level: int = 0


# Для рекурсивных ссылок
MaterialGroupTreeResponse.model_rebuild()