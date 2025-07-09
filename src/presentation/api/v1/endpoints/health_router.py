from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", summary="Health check", response_description="API is healthy")
async def health_check():
    return JSONResponse(content={"status": "ooookkk"})
