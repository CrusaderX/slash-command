from re import sub
from enum import Enum
from typing import Any, Tuple

from src.models.slack_model import StatusEnums
from src.services.base_action_service import BaseAction
from src.handlers.error_handler import DevenvSupportSizeError


class Types(str, Enum):
    XL = "8192Mi"
    L = "4096Mi"
    M = "2048Mi"
    S = "1024Mi"
    XS = "512Mi"

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls.__members__


class SupportAction(BaseAction):
    def parse(self, text: str) -> None:
        # assume command is /devenv support <action> <name> <Optional: size>
        self.action, self.command, self.name, *self.options = text.split(" ")
        # hadcode namespace for now
        self.namespace = "support"

    def validate(self) -> None:
        self.name = sub(r"[^a-zA-Z0-9-]", "", self.name)
        self.size = Types.S

        if self.options:
            size, *_ = self.options
            size = size.upper()

            if not Types.has(size):
                raise DevenvSupportSizeError(size=size)

            self.size = Types[size]

    def execute(self) -> dict:
        return {"action": self.command, "size": self.size, "name": self.name}

    def slack_response(self, response: dict, status_code: int | None = None) -> dict:
        details = response.get("detail", None)

        error_details = {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "text": f"Something went wrong",
                        "type": "mrkdwn",
                    },
                    "fields": [
                        {"type": "mrkdwn", "text": "*Details*"},
                        {"type": "mrkdwn", "text": "*Status*"},
                        {
                            "type": "mrkdwn",
                            "text": f"{details}",
                        },
                        {
                            "type": "plain_text",
                            "text": f"{status_code}",
                        },
                    ],
                },
            ],
        }

        response = {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "text": f"Manage job {self.name} is {StatusEnums[self.command.upper()].value} in {self.namespace} namespace with size {self.size}.",
                        "type": "mrkdwn",
                    },
                },
            ],
        }

        if details:
            return error_details

        return response

# Example of remoter scaler

#    async def scaler_response(
#        self,
#        json: dict,
#    ) -> Tuple[Any, int]:
#        scaler_url = "https://remote.example.com/api/v1"
#        return await super().scaler_response(scaler_url=scaler_url, json=json)
