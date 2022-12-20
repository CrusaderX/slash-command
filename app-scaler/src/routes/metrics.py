from fastapi import APIRouter

from ..controllers import (
    metrics_controller,
)

metric_router = APIRouter()

metric_router.include_router(metrics_controller.router)
