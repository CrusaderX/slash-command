from http import HTTPStatus
from re import sub
from aiohttp import ClientSession
from typing import Optional

from ..models.slack_model import ActionEnums
from ..handlers.error_handler import (
    DevenvActionIsNotImplementedError,
    ScalerEndpointUnhealthyError,
    DevenvNamespaceIsNotAllowedError,
    DevenvArgumentListTooBigError,
    DevenvProlongateWrongTimeError,
)
from ..controllers.metrics_controller import PrometheusMetrics
from .slack_service import SlackResponses
from .notification_service import NotificationService
from ..config import settings

notification_service = NotificationService()
slack_responses = SlackResponses()


class DevenvService:
    def __init__(self, text: str) -> None:
        self._action, *params = text.split(" ")

        try:
            ActionEnums[self._action.upper()]
        except:
            raise DevenvActionIsNotImplementedError(action=self._action)

        if params:
            _, namespace, *prolongate = text.split(" ")
            self._namespace = namespace
            self._prolongate = prolongate

            if self._namespace not in settings.namespaces:
                raise DevenvNamespaceIsNotAllowedError(namespace=self._namespace)

            if self._prolongate.__len__() > 2:
                raise DevenvArgumentListTooBigError(text=text)

    def generate_body_for_action(self) -> dict:
        """
        here we trying to match slack slach command action to real
        action that would be taken against app-scaler
        """
        if self._action == ActionEnums.HELP:
            return {}

        if self._action == ActionEnums.STATUS:
            return {"namespace": self._namespace}

        if self._action == ActionEnums.START:
            PrometheusMetrics.start_command_total.inc()
            return {"namespaces": [self._namespace], "replicas": 1}

        if self._action == ActionEnums.STOP:
            PrometheusMetrics.stop_command_total.inc()
            return {"namespaces": [self._namespace], "replicas": 0}

        if self._action == ActionEnums.PROLONGATE:
            hours = self._prolongate.pop()
            hours = int(sub(settings.pattern, "", hours))

            if 24 < hours <= 0:
                raise DevenvProlongateWrongTimeError(hours=hours)

            PrometheusMetrics.prolongate_command_total.inc()
            PrometheusMetrics.prolongate_hours_total.inc(hours)

            notification_service.update_default_notification_slot(
                namespace=self._namespace, hours=hours
            )

            return {"namespace": self._namespace, "hours": hours}

    async def send_request(
        self,
        json: dict = {},
        headers: dict = {"content-type": "application/json"},
    ) -> dict:
        """
        if there is no payload -> don't do any request
        """
        if not json:
            return

        url = f"{settings.scaler_url}/{self._action}"
        params = {
            "url": url,
            "json": json,
            "headers": headers,
        }
        async with ClientSession() as session:
            async with session.post(**params) as response:
                if response.status != HTTPStatus.CREATED:
                    raise ScalerEndpointUnhealthyError(response.status, response.text)
                return await response.json()

    def slack_response(self, response: Optional[dict] = {}) -> dict:
        if self._action in [
            ActionEnums.START,
            ActionEnums.STOP,
            ActionEnums.PROLONGATE,
        ]:
            return slack_responses.send_basic_operations_response(
                slack_namespace=self._namespace, action=self._action
            )
        if self._action in ActionEnums.STATUS:
            return slack_responses.send_status_operation_response(
                slack_namespace=self._namespace, status=response["status"]
            )
        return slack_responses.send_default_operation_response()
