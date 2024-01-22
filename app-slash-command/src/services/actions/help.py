from http import HTTPStatus
from typing import Tuple, Any

from src.services.base_action_service import BaseAction
from src.services.slack_service import SlackResponses


class HelpAction(BaseAction):
    def parse(self, _) -> None:
        pass

    def validate(self) -> None:
        pass

    def execute(self) -> None:
        pass

    async def scaler_response(
        self,
        **_,
    ) -> Tuple[dict, HTTPStatus]:
        return {}, HTTPStatus.OK

    def slack_response(self, **_) -> dict[Any, Any]:
        return SlackResponses.send_default_operation_response()
