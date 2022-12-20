from typing import Dict, List, Optional, Generator
from operator import gt, ge

from ..services.base_service import BaseComponents
from ..handlers.error_handler import ScalerCronJobNameHasChangedError
from ..models.scaler_model import StatusEnums
from ..config import settings


class ScalerService(BaseComponents):
    CRON_MAX_HOUR = 23

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, replicas: int) -> None:
        if replicas > 0:
            self._action = ge
        else:
            self._action = gt

    def describe(
        self,
        kinds: List[str],
        namespaces: List[str],
        label_selector: Optional[str] = None,
    ) -> Generator[List, None, None]:
        """
        Get given kinds across provided namespaces, kinds are from models/scalerModel

        :param kinds: List[str] which kinds should we call with getattr
        :param namespaces: List[str] namespaces where to find kinds
        :param label_selector: Optional[str] provided label for signle query

        :return Generator[List, None, None]:
        """
        for kind in kinds:
            yield getattr(self, kind)(
                namespaces=namespaces, label_selector=label_selector
            )

    def filter(self, kind: Dict, exclude: Optional[List[str]] = []) -> List[Dict]:
        """
        Filter given kinds to exclude

        :param kinds: List[str]
        :param exclude: Optional[List[str]] which deployment or statefulsets should we exclude from our result

        :return List[Dict]
        """
        return [
            {
                k: {
                    namespace: {
                        name: replicas
                        for name, replicas in statuses.items()
                        if self.action(replicas, 0) and name not in exclude
                    }
                    for namespace, statuses in _.items()
                }
            }
            for k, _ in kind.items()
        ]

    def patch(
        self,
        kind: Dict,
        body: dict,
    ) -> None:
        """
        :param kinds: List[str]
        :param namespaces: List[str] namespaces where to find kinds
        :param replicas: int desired replica count for kind

        :return None
        """
        for k, v in kind.items():
            for namespace, statuses in v.items():
                if not statuses:
                    continue
                for name in statuses:
                    getattr(self, f"patch_{k}")(
                        name=name, namespace=namespace, body=body
                    )

    def status(self, kind: str, namespace: str, name: str) -> dict:
        response = self.kind_status(
            kind=kind,
            name=name,
            namespace=namespace,
        )
        try:
            replicas = response.spec.replicas
            ready = response.status.ready_replicas
            not_ready = response.status.unavailable_replicas
        except AttributeError:
            return StatusEnums.NOT_FOUND

        if replicas < 1:
            return StatusEnums.STOPPED

        if not_ready:
            return StatusEnums.PENDING

        if replicas >= 1 and ready > 0:
            return StatusEnums.RUNNING

    @staticmethod
    def modify_schedule(cronjob: dict, namespace: str, hours: int) -> str:
        try:
            schedule = cronjob["cronjobs"][namespace][settings.cron_job_default_label]
        except KeyError:
            raise ScalerCronJobNameHasChangedError(name=settings.cron_job_default_label)

        minute, hour, day, month, week, *other = schedule.split()

        assert not other

        hour = int(hour)

        if hours + hour > ScalerService.CRON_MAX_HOUR:
            hour = hours - (ScalerService.CRON_MAX_HOUR - hour) - 1
        else:
            hour = hour + hours

        return f"{minute} {hour} {day} {month} {week}"
