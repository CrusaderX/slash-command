from http import HTTPStatus
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from .errors import ScalerError
from ..config import settings
from ..models.cronjob_model import (
    AdmissionWebhookResponseModel,
    ResponseModel,
    StatusModel,
    LabelEnums,
    OperationEnums,
)


class ScalerBadNamespaceLabelError(ScalerError):
    def __init__(self, uid: str):
        self.status = HTTPStatus.BAD_REQUEST
        self.uid = uid
        self.message = f"Currently we support only {LabelEnums.__members__} labels"


class ScalerOperationNotSupportedError(ScalerError):
    def __init__(self, uid: str):
        self.status = HTTPStatus.BAD_REQUEST
        self.uid = uid
        self.message = (
            f"Currently we support only {OperationEnums.__members__} operations"
        )


class ScalerDynamodbMissingDataError(ScalerError):
    def __init__(self, fetcher_id: str):
        self.status = HTTPStatus.NOT_FOUND
        self.fetcher_id = fetcher_id
        self.message = f"Couln't find data in dynamodb for {fetcher_id} fetcher_id in {settings.cacher_state_table} table name"


async def scaler_validation_handler(
    request: Request, exc: ScalerBadNamespaceLabelError
):
    status = StatusModel(
        code=HTTPStatus.BAD_REQUEST,
        message=exc.message,
    )
    response = ResponseModel(uid=exc.uid, allowed=False, status=status)
    content = jsonable_encoder(
        AdmissionWebhookResponseModel(response=response),
    )

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=content,
    )
