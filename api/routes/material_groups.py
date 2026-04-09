"""
Эндпоинты для работы с группами материалов
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
import logging

from application.dto.material_group_dto import (
    MaterialGroupCreate,
    MaterialGroupUpdate,
    MaterialGroupResponse,
    MaterialGroupTreeResponse
)
from infrastructure.repositories.material_group_repository import material_group_repository
from api.middleware.auth import get_admin_user, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/material-groups", tags=["Material Groups"])


@router.get(
    "/",
    response_model=List[MaterialGroupResponse],
    summary="Список групп",
    description="Возвращает список всех групп материалов"
)
async def get_all_groups(current_user: dict = Depends(get_current_user)):
    """Получить все группы материалов (требует авторизации)"""
    groups = await material_group_repository.get_all()
    return groups


@router.get(
    "/tree",
    response_model=List[MaterialGroupTreeResponse],
    summary="Дерево групп",
    description="Возвращает древовидную структуру групп материалов"
)
async def get_groups_tree(current_user: dict = Depends(get_current_user)):
    """Получить дерево групп материалов (требует авторизации)"""
    tree = await material_group_repository.get_tree()
    return tree


@router.get(
    "/{group_id}",
    response_model=MaterialGroupResponse,
    summary="Группа по ID",
    description="Возвращает информацию о группе материалов"
)
async def get_group_by_id(
    group_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Получить группу по ID (требует авторизации)"""
    group = await material_group_repository.get_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    return group


@router.get(
    "/{group_id}/children",
    response_model=List[MaterialGroupResponse],
    summary="Дочерние группы",
    description="Возвращает дочерние группы указанной группы"
)
async def get_children_groups(
    group_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Получить дочерние группы (требует авторизации)"""
    children = await material_group_repository.get_children(group_id)
    return children


@router.get(
    "/{group_id}/path",
    summary="Путь к группе",
    description="Возвращает путь от корня до указанной группы"
)
async def get_group_path(
    group_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Получить путь к группе (требует авторизации)"""
    group = await material_group_repository.get_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    
    path = await material_group_repository.get_path(group_id)
    return {"path": path}


# ============ Административные эндпоинты (только admin) ============

@router.post(
    "/",
    response_model=MaterialGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать группу",
    description="Создание новой группы материалов (требует прав администратора)"
)
async def create_group(
    group_data: MaterialGroupCreate,
    current_user: dict = Depends(get_admin_user)
):
    """Создать новую группу материалов (только admin)"""
    try:
        if group_data.parent_id:
            parent = await material_group_repository.get_by_id(group_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent group with id {group_data.parent_id} not found"
                )
        
        group_id = await material_group_repository.create(
            name=group_data.name,
            parent_id=group_data.parent_id
        )
        
        new_group = await material_group_repository.get_by_id(group_id)
        
        logger.info(f"Admin {current_user['login']} created material group: {group_data.name}")
        
        return new_group
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{group_id}",
    response_model=MaterialGroupResponse,
    summary="Обновить группу",
    description="Обновление информации о группе (требует прав администратора)"
)
async def update_group(
    group_id: int,
    group_data: MaterialGroupUpdate,
    current_user: dict = Depends(get_admin_user)
):
    """Обновить группу материалов (только admin)"""
    existing = await material_group_repository.get_by_id(group_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    
    if group_data.parent_id:
        if group_data.parent_id == group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set group as its own parent"
            )
        
        parent = await material_group_repository.get_by_id(group_data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent group with id {group_data.parent_id} not found"
            )
    
    try:
        success = await material_group_repository.update(
            group_id=group_id,
            name=group_data.name,
            parent_id=group_data.parent_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )
        
        updated_group = await material_group_repository.get_by_id(group_id)
        
        logger.info(f"Admin {current_user['login']} updated material group: id={group_id}")
        
        return updated_group
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{group_id}",
    summary="Удалить группу",
    description="Удаление группы материалов (требует прав администратора)"
)
async def delete_group(
    group_id: int,
    current_user: dict = Depends(get_admin_user)
):
    """Удалить группу материалов (только admin)"""
    existing = await material_group_repository.get_by_id(group_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    
    try:
        success = await material_group_repository.delete(group_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )
        
        logger.info(f"Admin {current_user['login']} deleted material group: id={group_id}, name={existing['name']}")
        
        return {"message": f"Group '{existing['name']}' deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )