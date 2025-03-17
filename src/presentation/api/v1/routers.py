from fastapi import APIRouter

from .endpoints import users
from .endpoints import shooter
from .endpoints import auth_router as auth
from .endpoints import shooting_club_router as shooting_club
from .endpoints import target_router as target
router = APIRouter()

router.include_router(users.router)
router.include_router(shooter.router)
router.include_router(auth.router)
router.include_router(shooting_club.router)
router.include_router(target.router)
