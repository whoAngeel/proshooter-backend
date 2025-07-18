from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Path,
    status,
    Body,
    UploadFile,
)
from typing import List, Optional

from src.application.services.target_images_service import TargetImagesService
from src.presentation.schemas.target_images_schema import (
    TargetImageCreate,
    TargetImageDetail,
    TargetImageUpdate,
)
from src.infraestructure.auth.jwt_config import get_current_user
from src.presentation.schemas.user_schemas import UserRead
from src.domain.enums.role_enum import RoleEnum

router = APIRouter(
    prefix="/exercises/target-images",
    tags=["target-images"],
    responses={404: {"description": "Not found"}},
)

# @router.post("/upload")
# async def upload_target_image
