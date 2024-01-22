from fastapi import APIRouter, Depends, Header
from http import HTTPStatus

from ..models.slack_model import SlackSlashCommandModel
from ..services.notification_service import NotificationService
from ..services.actions_factory import ActionFactory
from ..services.slack_service import SlackService
from ..common.utils import logger
from ..handlers.errors import SlackBotError

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

    action, *_ = payload.text.split(" ")
    action_service = ActionFactory.create_action(action)
    action_service.parse(payload.text)
    action_service.validate()
    json = action_service.execute()
    response, status_code = await action_service.scaler_response(json=json)

    return action_service.slack_response(response=response, status_code=status_code)


@router.post("/devenv/slack/notifications", status_code=HTTPStatus.CREATED)
async def slack_notifications():
    notification_service.set_default_notifications_slots()
