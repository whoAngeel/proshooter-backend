from fastapi import APIRouter

from .endpoints import users
from .endpoints import shooter

router = APIRouter()

router.include_router(users.router)
router.include_router(shooter.router)
