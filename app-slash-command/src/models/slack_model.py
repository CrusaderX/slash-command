from pydantic import BaseModel
from fastapi import Form
from enum import Enum


class ActionEnums(str, Enum):
    STOP = "stop"
    START = "start"
    PROLONGATE = "prolongate"
    HELP = "help"
    STATUS = "status"
    SUPPORT = "support"


class StatusEnums(str, Enum):
    STOP = "stopping"
    START = "starting"
    PROLONGATE = "prolongated"


def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls


@form_body
class SlackSlashCommandModel(BaseModel):
    token: str
    team_id: str
    team_domain: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    command: str
    text: str
    api_app_id: str
    is_enterprise_install: str
    response_url: str
    trigger_id: str
