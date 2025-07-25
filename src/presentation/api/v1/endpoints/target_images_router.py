from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from uuid import UUID
from src.application.services.target_images_service import TargetImagesService
from src.infraestructure.database.session import get_db
from sqlalchemy.orm import Session
import io
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
    prefix="/target-images",
    tags=["target-images"],
    responses={404: {"description": "Not found"}},
)


# @router.post("/upload")
# async def upload_target_image
@router.get("/images/{image_id}/with-impacts", response_class=StreamingResponse)
def get_image_with_impacts(
    image_id: UUID,
    db: Session = Depends(get_db),
):
    service = TargetImagesService(db)
    image_bytes, error = service.get_image_with_impacts(image_id)
    if error or not image_bytes:
        return Response(content=error or "Error generando imagen", status_code=404)
    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/jpeg")
