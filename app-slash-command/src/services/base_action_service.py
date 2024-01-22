from http import HTTPStatus
from aiohttp import ClientSession, ClientConnectorError
from typing import Any, Tuple
from abc import ABC, abstractmethod

from ..handlers.error_handler import (
    ScalerEndpointUnhealthyError,
)
from .slack_service import SlackResponses
from .notification_service import NotificationService
from ..config import settings

notification_service = NotificationService()
slack_responses = SlackResponses()


class Action(ABC):
    @abstractmethod
    def parse(self, text: str) -> None:
        pass

    @abstractmethod
    def validate(self) -> None:
        pass

    @abstractmethod
    def execute(self) -> dict[Any, Any]:
        pass

    @abstractmethod
    def slack_response(
        self, response: dict, status_code: int | None = None
    ) -> dict[Any, Any]:
        pass

    @abstractmethod
    async def scaler_response(
        self,
        action: str | None = None,
        json: dict = {},
        headers: dict = {
            "Content-Type": "application/json",
            "X-Slack-Bot-Request": "app-slack-bot",
        },
    ) -> Tuple[Any, int]:
        pass


class BaseAction(Action):
    def parse(self, text: str) -> None:
        self.action, self.namespace, *self.unused = text.split(" ")

    def validate(self) -> None:
        if self.namespace in settings.namespaces and settings.namespace_prefix:
            self.namespace = "-".join([settings.namespace_prefix, self.namespace])

    def execute(self) -> dict[Any, Any]:
        return {}

    def slack_response(
        self, response: dict, status_code: int | None = None
    ) -> dict[Any, Any]:
        return SlackResponses.send_basic_operations_response(
            slack_namespace=self.namespace,
            action=self.action,
            details=response.get("detail", ""),
            status_code=status_code,
        )

    async def scaler_response(
        self,
        scaler_url: str | None = None,
        json: dict = {},
        headers: dict = {
            "Content-Type": "application/json",
            "X-Slack-Bot-Request": "app-slack-bot",
        },
    ) -> Tuple[Any, int]:

        scaler_url = scaler_url or settings.scaler_url

        url = f"{scaler_url}/{self.action}"
        params = {
            "url": url,
            "json": json,
            "headers": headers,
        }

        async with ClientSession() as session:
            try:
                async with session.post(**params) as response:
                    return await response.json(), response.status
            except ClientConnectorError as e:
                raise ScalerEndpointUnhealthyError(
                    HTTPStatus.INTERNAL_SERVER_ERROR, str(e)
                )
