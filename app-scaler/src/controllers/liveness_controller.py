from fastapi import APIRouter
from http import HTTPStatus

router = APIRouter(prefix="/liveness")


@router.get("/", status_code=HTTPStatus.OK)
async def liveness():
    return {"status": "healthy"}
