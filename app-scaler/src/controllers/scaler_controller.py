from fastapi import APIRouter, Header, BackgroundTasks
from http import HTTPStatus
from typing import cast

from ..models.scaler_model import (
    PayloadFieldsEnums,
    ScalerModel,
    ScalerProlongateModel,
    ScalerProlongateResponseModel,
    ScalerScheduleResetModel,
    ScalerScheduleResetResponseModel,
    ScalerStatusModel,
    ScalerSupportModel,
)
from ..services.scaler_service import ScalerService
from ..services.support_service import SupportService
from ..services.aws_service import AwsService
from ..common.utils import logger

scaler = ScalerService()
aws = AwsService()
support_service = SupportService()

router = APIRouter(
    prefix="/api/v1",
    responses={HTTPStatus.NOT_FOUND: {"message": "not found"}},
)


@router.post("/start", status_code=HTTPStatus.CREATED)
@router.post("/stop", status_code=HTTPStatus.CREATED)
async def scale(
    model: ScalerModel,
    background_tasks: BackgroundTasks,
    x_slack_bot_request: str = Header(None),
):
    """
    Scale deployment or statefulset based on provided replica count
    """
    scaler.action = model.replicas

    logger.info(
        f"Got request with kinds: {model.kinds} in {model.namespaces} namespaces, should scale to {model.replicas} replicas"
    )

    background_tasks.add_task(
        aws.start_stop_instances,
        replicas=model.replicas,
        namespaces=model.namespaces,
        header=x_slack_bot_request,
    )

    kinds = list(scaler.describe(kinds=model.kinds, namespaces=model.namespaces))

    for kind in kinds:
        scaler.patch(
            kind=scaler.filter(kind=kind, exclude=model.exclude).pop(),
            body={"spec": {PayloadFieldsEnums.DEPLOYMENT: model.replicas}},
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
        cronjob=cast(dict, cronjob),
        namespace=model.namespace,
        hours=model.hours,
    )

    scaler.patch(
        kind=cast(dict, cronjob), body={"spec": {PayloadFieldsEnums.CRON_JOB: schedule}}
    )

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
        kind=cast(dict, cronjobs),
        body={"spec": {PayloadFieldsEnums.CRON_JOB: model.schedule}},
    )

    return model


@router.post("/status", status_code=HTTPStatus.CREATED)
async def status(model: ScalerStatusModel):

    logger.info(
        f"Got request with kind: {model.kind} in {model.namespace} namespace and status request"
    )

    return {
        "status": scaler.status(
            kind=model.kind,
            name=model.label_selector,
            namespace=model.namespace,
        )
    }


@router.post("/support", status_code=HTTPStatus.CREATED)
async def support(model: ScalerSupportModel):
    (job,) = list(
        scaler.describe(
            kinds=[model.kind],
            label_selector=f"app={model.name}",
            namespaces=[model.namespace],
        )
    )
    support_service.validate(
        action=model.action,
        job=cast(dict, job),
        name=model.name,
        namespace=model.namespace,
    )
    support_service.create_or_delete(
        action=model.action,
        name=model.name,
        namespace=model.namespace,
        size=model.size,
    )

    return model
