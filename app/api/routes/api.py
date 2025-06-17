from fastapi import APIRouter

from app.core.config import settings

from . import auth, docs, reset, user

auth.router.include_router(reset.router)

router = APIRouter(prefix=f"/api/{settings.API_V1_STR}")
router.include_router(docs.router)
router.include_router(auth.router)
router.include_router(user.router)
