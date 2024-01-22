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
    def send_basic_operations_response(
        slack_namespace: str,
        action: str,
        details: str | None = None,
        status_code: int | None = None,
    ) -> dict:
        additional_text = str()

        if (
            action
            in [
                ActionEnums.START,
                ActionEnums.STOP,
            ]
            and slack_namespace in settings.namespaces_with_depth
        ):
            additional_text = " Please, wait additional 5-10m, aws services (ec2, rds) are launching/stopping."

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
                }
            ],
        }

        response = {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "text": f"Environment *{slack_namespace}* is {StatusEnums[action.upper()].value}.{additional_text}",
                        "type": "mrkdwn",
                    },
                    "fields": [
                        {"type": "mrkdwn", "text": "*URL*"},
                        {"type": "mrkdwn", "text": "*Status*"},
                        {
                            "type": "mrkdwn",
                            "text": f"https://{slack_namespace}.example.com",
                        },
                        {
                            "type": "plain_text",
                            "text": f"{StatusEnums[action.upper()].value}",
                        },
                    ],
                },
            ],
        }

        if details:
            return error_details

        return response

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
                            "text": "/devenv prolongate dev1 for 1h",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"{list(ActionEnums._member_map_.keys())}",
                        },
                    ],
                },
            ],
        }
