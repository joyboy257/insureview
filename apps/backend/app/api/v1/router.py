from fastapi import APIRouter

from app.api.v1 import auth, policies, upload, parse, analysis

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(policies.router, prefix="/policies", tags=["policies"])
router.include_router(upload.router, prefix="/upload", tags=["upload"])
router.include_router(parse.router, prefix="/parse", tags=["parse"])
router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
