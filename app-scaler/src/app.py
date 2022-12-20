from fastapi import FastAPI
from uvicorn import run

from .routes.scaler import scaler_router
from .routes.metrics import metric_router
from .routes.liveness import healthz_router
from .handlers.validation_handler import (
    ScalerBadNamespaceLabelError,
    ScalerOperationNotSupportedError,
    scaler_validation_handler,
)

app = FastAPI()

app.include_router(scaler_router)
app.include_router(metric_router)
app.include_router(healthz_router)

app.add_exception_handler(ScalerBadNamespaceLabelError, scaler_validation_handler)
app.add_exception_handler(ScalerOperationNotSupportedError, scaler_validation_handler)


def start():
    run("src.app:app", host="0.0.0.0", port=3086, reload=True)
