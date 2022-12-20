from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import (
    generate_latest,
    Counter,
    REGISTRY,
    PROCESS_COLLECTOR,
    PLATFORM_COLLECTOR,
)

router = APIRouter(prefix="/api/v1")

REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(REGISTRY._names_to_collectors["python_gc_objects_collected_total"])


class PrometheusMetrics:
    stop_command_total = Counter("stop_command_total", "")
    start_command_total = Counter("start_command_total", "")
    prolongate_command_total = Counter(
        "prolongate_command_total",
        "",
    )
    prolongate_hours_total = Counter("prolongate_hours_total", "")


@router.get("/metrics")
async def metrics():
    return Response(
        generate_latest(), media_type="text/plain; version=0.0.4; charset=utf-8"
    )
