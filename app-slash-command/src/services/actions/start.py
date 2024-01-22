from src.controllers.metrics_controller import PrometheusMetrics
from src.services.base_action_service import BaseAction


class StartAction(BaseAction):
    def execute(self) -> dict:
        PrometheusMetrics.start_command_total.inc()

        return {"namespaces": [self.namespace], "replicas": 1}
