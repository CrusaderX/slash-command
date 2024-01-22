from src.services.base_action_service import BaseAction
from src.services.slack_service import SlackResponses


class StatusAction(BaseAction):
    def execute(self) -> dict:
        return {"namespace": self.namespace}

    def slack_response(self, response: dict, **_) -> dict:
        return SlackResponses.send_status_operation_response(
            slack_namespace=self.namespace,
            status=response.get("status", None),
        )
