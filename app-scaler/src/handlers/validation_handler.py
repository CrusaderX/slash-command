from http import HTTPStatus
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from ..models.cronjob_model import (
    AdmissionWebhookResponseModel,
    ResponseModel,
    StatusModel,
    LabelEnums,
    OperationEnums,
)


class ScalerBadNamespaceLabelError(Exception):
    def __init__(self, uid: str):
        self.uid = uid
        self.message = f"Currently we support only {LabelEnums.__members__} labels"


class ScalerOperationNotSupportedError(Exception):
    def __init__(self, uid: str):
        self.uid = uid
        self.message = (
            f"Currently we support only {OperationEnums.__members__} operations"
        )


async def scaler_validation_handler(
    request: Request, exc: ScalerBadNamespaceLabelError
):
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=jsonable_encoder(
            AdmissionWebhookResponseModel(
                response=ResponseModel(
                    uid=exc.uid,
                    allowed=False,
                    status=StatusModel(
                        code=HTTPStatus.BAD_REQUEST,
                        message=exc.message,
                    ),
                )
            ),
        ),
    )
