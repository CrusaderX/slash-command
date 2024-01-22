from re import sub

from src.controllers.metrics_controller import PrometheusMetrics
from src.services.base_action_service import BaseAction
from src.handlers.error_handler import (
    DevenvArgumentListTooBigError,
    DevenvProlongateWrongTimeError,
)
from src.config import settings
from src.services.notification_service import NotificationService


class ProlongateAction(BaseAction):
    def parse(self, text: str) -> None:
        self.action, self.namespace, *prolongate = text.split(" ")
        self.hours = int(sub(settings.pattern, "", prolongate.pop()))

        if 24 < self.hours <= 0:
            raise DevenvProlongateWrongTimeError(hours=self.hours)

        if prolongate.__len__() > 2:
            raise DevenvArgumentListTooBigError(text=text)

    def execute(self) -> dict:
        PrometheusMetrics.prolongate_command_total.inc()
        PrometheusMetrics.prolongate_hours_total.inc(self.hours)

        NotificationService.update_default_notification_slot(
            namespace=self.namespace, hours=self.hours
        )

        return {"namespace": self.namespace, "hours": self.hours}
