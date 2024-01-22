from src.controllers.metrics_controller import PrometheusMetrics
from src.services.base_action_service import BaseAction


class StopAction(BaseAction):
    def execute(self) -> dict:
        PrometheusMetrics.stop_command_total.inc()

        return {"namespaces": [self.namespace], "replicas": 0}
