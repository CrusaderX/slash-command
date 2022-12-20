from fastapi import APIRouter, Request
from http import HTTPStatus

from ..models.cronjob_model import (
    AdmissionWebhookResponseModel,
    ResponseModel,
)
from ..services.cronjob_service import CronjobService

cronjob_service = CronjobService()
router = APIRouter(
    prefix="/api/v1",
    responses={HTTPStatus.NOT_FOUND: {"message": "not found"}},
)


@router.post("/namespace", response_model=AdmissionWebhookResponseModel)
async def namespace(request: Request):
    """
    If it's an UPDATE or CREATE operation:
    - scheduler label is enabled -> create cronjob if doesn't exist, otherwise - unpause
    - scheduler label is disabled -> suspend cronjob if exists
    - scheduler label is missing -> do nothing

    Response model should be exact as provided in documentation, otherwise any operation
    will fail. Link: https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#response

    :params request: Request kubernetes payload that was sent by API

    :return AdmissionWebhookResponseModel
    """
    payload = await request.json()
    operation, uid, labels, namespace = cronjob_service.required_fields(payload=payload)
    cronjob_service.validate_operation(uid=uid, operation=operation)
    cronjob_service.create_or_update(uid=uid, labels=labels, namespace=namespace)

    return AdmissionWebhookResponseModel(response=ResponseModel(uid=uid))
