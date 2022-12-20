from fastapi import APIRouter

from ..controllers import scaler_controller, cronjob_controller

scaler_router = APIRouter()

scaler_router.include_router(scaler_controller.router)
scaler_router.include_router(cronjob_controller.router)
