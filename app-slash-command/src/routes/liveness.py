from fastapi import APIRouter

from ..controllers import (
    liveness_controller,
    readiness_controller,
)

healthz_router = APIRouter()

healthz_router.include_router(liveness_controller.router)
healthz_router.include_router(readiness_controller.router)
