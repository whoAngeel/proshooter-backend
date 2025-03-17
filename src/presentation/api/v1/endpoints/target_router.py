from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from typing import List, Optional
from uuid import UUID

from src.application.services.target_service import TargetService

from src.domain.enums.target_enum import TargetType
from src.domain.enums.role_enum import RoleEnum

from src.presentation.schemas.target_schema import *
from src.presentation.schemas.user_schemas import UserRead

from src.infraestructure.auth.jwt_config import get_current_user


router = APIRouter(
    prefix="/targets",
    tags=["targets"]
)

@router.post("/", response_model=TargetRead)
async def create_target(
    target_data: TargetCreate,
    target_service: TargetService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    '''
    Crea un nuevo blanco de tiro

    Solo Administradores pueden crear blancos
    '''

    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Solo administradores pueden crear blancos"
        )

    target, error = target_service.create_target(target_data)
    if error:
        raise HTTPException(status_code=400, detail=error)

    return target


@router.get("/", response_model=List[TargetRead])
async def get_all_targets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    target_type: Optional[TargetType] = Query(None),
    target_service: TargetService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    """
    Obtiene todos los blancos con opciones de filtrado.
    """
    if target_type:
        return target_service.get_targets_by_type(target_type)
    else:
        return target_service.get_all_targets(skip, limit, active_only)

@router.get("/search", response_model=List[TargetRead])
async def search_targets(
    term: str = Query(..., description="Search term to find in name or description"),
    target_service: TargetService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    """
    Searches for targets by matching the provided term in either name or description.

    This endpoint performs a case-insensitive search on both the name and description
    fields of the targets. Results include any target where the term appears in either field.
    """
    return target_service.search_targets_by_term(term)


@router.get("/{target_id}", response_model=TargetDetail)
async def get_target_detail(
    target_id: UUID = Path(..., title="ID del blanco"),
    target_service: TargetService = Depends(),
    current_user: UserRead = Depends(get_current_user)

):
    """
    Obtiene los detalles de un blanco por su ID.
    """
    target, error = target_service.get_target_detail(target_id)
    if error:
        raise HTTPException(status_code=404, detail=error)

    return target

@router.put("/{target_id}", response_model=TargetRead)
async def update_target(
    target_id: UUID = Path(...),
    target_data: TargetUpdate = None,
    target_service: TargetService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    """
    Actualiza un blanco existente.

    Solo administradores pueden actualizar blancos.
    """
    # Verificar permisos
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Solo administradores pueden actualizar blancos")

    target, error = target_service.update_target(target_id, target_data)
    if error:
        if error == "TARGET_NOT_FOUND":
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return target

@router.delete("/{target_id}")
async def delete_target(
    target_id: UUID = Path(...),
    soft_delete: bool = Query(True),
    target_service: TargetService = Depends(),
    current_user: UserRead = Depends(get_current_user)
):
    """
    Elimina o desactiva un blanco.

    Por defecto realiza una eliminación lógica (desactivación).
    Solo administradores pueden eliminar blancos.
    """
    # Verificar permisos
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar blancos")

    success, error = target_service.delete_target(target_id,  soft_delete)
    if error:
        if error == "TARGET_NOT_FOUND":
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return {
        "message": "Blanco eliminado correctamente",
        "id": target_id
            }
