from fastapi import APIRouter

from ..controllers import (
    apiv1_controller,
)

apiv1_router = APIRouter()

apiv1_router.include_router(apiv1_controller.router)
