from fastapi import APIRouter

from .endpoints import users
from .endpoints import shooter
from .endpoints import auth_router as auth
from .endpoints import shooting_club_router as shooting_club
from .endpoints import target_router as target
from .endpoints import weapon_router as weapon
from .endpoints import ammo_router as ammo
from .endpoints import profile_router as profile
from .endpoints import practice_type_router as practice_type
from .endpoints import practice_session_router as practice_session
from .endpoints import practice_exercise_router as practice_exercise
from .endpoints import practice_evaluation_router as practice_evaluation
from .endpoints import health_router as health
from .endpoints import analysis_image_router as analysis_image
from .endpoints import instructor_router as instructor
from .endpoints import target_images_router as target_images
from .endpoints import instructor_dashboard_router as instructor_dashboard

router = APIRouter()
router.include_router(health.router)
router.include_router(users.router)
router.include_router(shooter.router)
router.include_router(auth.router)
router.include_router(shooting_club.router)
router.include_router(target.router)
router.include_router(weapon.router)
router.include_router(ammo.router)
router.include_router(profile.router)
router.include_router(practice_type.router)
router.include_router(practice_session.router)
router.include_router(practice_exercise.router)
router.include_router(practice_evaluation.router)
router.include_router(analysis_image.router)
router.include_router(instructor.router)
router.include_router(target_images.router)
router.include_router(instructor_dashboard.router)
