from fastapi import APIRouter, Depends, Header
from http import HTTPStatus

from ..models.slack_model import SlackSlashCommandModel
from ..services.devenv_service import DevenvService
from ..services.notification_service import NotificationService
from ..services.slack_service import SlackService
from ..common.utils import logger

router = APIRouter(
    prefix="/api/v1",
    responses={HTTPStatus.NOT_FOUND: {"message": "not found"}},
)
notification_service = NotificationService()


@router.post("/devenv")
async def devenv(
    payload: SlackSlashCommandModel = Depends(SlackSlashCommandModel),
    x_slack_request_timestamp: str = Header(None),
    x_slack_signature: str = Header(None),
):
    """
    Slack slash command entrypoint:
    - parse incoming message
    - generate request body
    - return slack block response
    """
    slack_service = SlackService(
        timestamp=x_slack_request_timestamp, signature=x_slack_signature
    )
    slack_service.validate_request(payload=payload.dict())

    logger.info(
        f"Got {payload.command} command from {payload.user_name} user with text {payload.text}, trying to evaluate it"
    )

    devenv_service = DevenvService(text=payload.text)
    json = devenv_service.generate_body_for_action()

    response = await devenv_service.send_request(json=json)

    return devenv_service.slack_response(response=response)


@router.post("/devenv/slack/notifications", status_code=HTTPStatus.CREATED)
async def slack_notifications():
    notification_service.set_default_notifications_slots()
