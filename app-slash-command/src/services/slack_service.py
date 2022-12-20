from urllib.parse import urlencode
from slack_sdk.signature import SignatureVerifier

from ..handlers.error_handler import DevenvInvalidRequestError
from ..models.slack_model import StatusEnums, ActionEnums
from ..config import settings


class SlackService:
    def __init__(self, timestamp: str, signature: str) -> None:
        self._headers = {
            "X-Slack-Request-Timestamp": timestamp,
            "X-Slack-Signature": signature,
        }

    def validate_request(self, payload: dict):
        """
        Retrieve the X-Slack-Request-Timestamp header on the HTTP request, and the body of the request.
        Validate the request by slack_sdk.signature.SignatureVerifier

        https://api.slack.com/authentication/verifying-requests-from-slack

        """
        verifier = SignatureVerifier(settings.secret)
        body = urlencode(payload)

        if not verifier.is_valid_request(body=body, headers=self._headers):
            raise DevenvInvalidRequestError


class SlackResponses:
    @staticmethod
    def send_basic_operations_response(slack_namespace: str, action: str) -> dict:
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "text": f"Environment *{slack_namespace}* is {StatusEnums[action.upper()].value}",
                        "type": "mrkdwn",
                    },
                    "fields": [
                        {"type": "mrkdwn", "text": "*Status*"},
                        {
                            "type": "plain_text",
                            "text": f"{StatusEnums[action.upper()].value}",
                        },
                    ],
                },
            ],
        }

    @staticmethod
    def send_status_operation_response(slack_namespace: str, status: str) -> dict:
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "text": f"Environment *{slack_namespace}* is {status}",
                        "type": "mrkdwn",
                    },
                },
            ],
        }

    @staticmethod
    def send_default_operation_response():
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "text": "Please, use slash command like /devenv <action> <namespace> [for <h>]",
                        "type": "mrkdwn",
                    },
                    "fields": [
                        {"type": "mrkdwn", "text": "*example*"},
                        {"type": "mrkdwn", "text": "*actions*"},
                        {
                            "type": "plain_text",
                            "text": "/devenv prolongate orca for 1h",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"{list(ActionEnums._member_map_.keys())}",
                        },
                    ],
                },
            ],
        }
