from fastapi import APIRouter
from http import HTTPStatus

from ..models.scaler_model import (
    PayloadFiledsEnums,
    ScalerModel,
    ScalerResponseModel,
    ScalerProlongateModel,
    ScalerProlongateResponseModel,
    ScalerScheduleResetModel,
    ScalerScheduleResetResponseModel,
    ScalerStatusModel,
)
from ..services.scaler_service import ScalerService
from ..common.utils import logger

scaler = ScalerService()
router = APIRouter(
    prefix="/api/v1",
    responses={HTTPStatus.NOT_FOUND: {"message": "not found"}},
)


@router.post(
    "/start", response_model=ScalerResponseModel, status_code=HTTPStatus.CREATED
)
@router.post(
    "/stop", response_model=ScalerResponseModel, status_code=HTTPStatus.CREATED
)
async def scale(model: ScalerModel):
    """
    Scale deployment or statefulset based on provided replica count
    """
    scaler.action = model.replicas

    logger.info(
        f"Got request with kinds: {model.kinds} in {model.namespaces} namespaces, should scale to {model.replicas} replicas"
    )

    kinds = list(scaler.describe(kinds=model.kinds, namespaces=model.namespaces))

    for kind in kinds:
        scaler.filter(kind=kind, exclude=model.exclude)
        scaler.patch(
            kind=kind, body={"spec": {PayloadFiledsEnums.DEPLOYMENT: model.replicas}}
        )

    return model


@router.post(
    "/prolongate",
    response_model=ScalerProlongateResponseModel,
    status_code=HTTPStatus.CREATED,
)
async def prolongate(model: ScalerProlongateModel):
    """
    Modify kubernetes crontjob to another timeslot. We grab first element of list,
    get the current timestamp and add to it requested hours
    """
    logger.info(
        f"Got request with kind: {model.kind} in {model.namespace} namespace, should modify cronjob schedule to run in {model.hours} hour(s)"
    )

    (cronjob,) = list(
        scaler.describe(
            kinds=[model.kind],
            namespaces=[model.namespace],
            label_selector=model.label_selector,
        )
    )
    schedule = scaler.modify_schedule(
        cronjob=cronjob, namespace=model.namespace, hours=model.hours
    )

    scaler.patch(kind=cronjob, body={"spec": {PayloadFiledsEnums.CRON_JOB: schedule}})

    return model


@router.post(
    "/schedule/reset",
    response_model=ScalerScheduleResetResponseModel,
    status_code=HTTPStatus.CREATED,
)
async def reset(model: ScalerScheduleResetModel):
    """
    Reset cronjobs schedule time to default
    """
    (cronjobs,) = list(
        scaler.describe(
            kinds=[model.kind],
            namespaces=model.namespaces,
            label_selector=model.label_selector,
        )
    )

    scaler.patch(
        kind=cronjobs, body={"spec": {PayloadFiledsEnums.CRON_JOB: model.schedule}}
    )

    return model


@router.post("/status", status_code=HTTPStatus.CREATED)
async def scale(model: ScalerStatusModel):

    logger.info(
        f"Got request with kind: {model.kind} in {model.namespace} namespace and status request"
    )

    return {
        "status": scaler.status(
            kind=model.kind,
            namespace=model.namespace,
            name=f"{model.namespace}-{model.label_selector}",
        )
    }
