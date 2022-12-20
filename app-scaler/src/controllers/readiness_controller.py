from fastapi import APIRouter
from http import HTTPStatus

router = APIRouter(
    prefix="/readiness",
)


@router.get("/", status_code=HTTPStatus.OK)
async def readiness():
    return {"status": "ready"}
