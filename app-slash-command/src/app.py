from fastapi import FastAPI
from uvicorn import run

from .routes.apiv1 import apiv1_router
from .routes.metrics import metric_router
from .routes.liveness import healthz_router

app = FastAPI()

app.include_router(apiv1_router)
app.include_router(metric_router)
app.include_router(healthz_router)


def start():
    run("src.app:app", host="0.0.0.0", port=3086, reload=True)
