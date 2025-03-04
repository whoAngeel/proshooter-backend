from fastapi import APIRouter

from .endpoints import users
from .endpoints import shooter
from .endpoints import auth_router as auth

router = APIRouter()

router.include_router(users.router)
router.include_router(shooter.router)
router.include_router(auth.router)
