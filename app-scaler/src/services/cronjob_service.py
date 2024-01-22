from typing import Tuple
from jinja2 import Template
from yaml import load, SafeLoader

from ..services.base_service import BaseComponents
from ..handlers.validation_handler import (
    ScalerBadNamespaceLabelError,
    ScalerOperationNotSupportedError,
)
from ..models.cronjob_model import OperationEnums, LabelEnums
from ..templates.cronjob import cronjob_template
from ..config import settings
from ..common.utils import logger


class CronjobService(BaseComponents):
    @staticmethod
    def required_fields(payload: dict) -> Tuple[str, str, str, str]:
        """
        these objects are always present, we shouldn't care about
        them absent
        """
        return (
            payload["request"]["operation"],
            payload["request"]["uid"],
            payload["request"]["object"]["metadata"]["labels"],
            payload["request"]["namespace"],
        )

    @staticmethod
    def validate_operation(uid: str, operation: str) -> None:
        try:
            OperationEnums[operation.upper()]
        except:
            raise ScalerOperationNotSupportedError(uid=uid)

    def create_or_update(self, uid: str, labels: dict, namespace: str) -> None:
        if settings.namespace_label in labels:
            label = labels[settings.namespace_label]

            try:
                LabelEnums[label.upper()]
            except:
                raise ScalerBadNamespaceLabelError(uid=uid)

            if label == LabelEnums.DISABLED:
                self.disable_scheduler(
                    name=settings.cron_job_default_label,
                    namespace=namespace,
                )

            if label == LabelEnums.ENABLED:
                self.enable_scheduler(
                    name=settings.cron_job_default_label,
                    namespace=namespace,
                )
        else:
            self.disable_scheduler(
                name=settings.cron_job_default_label,
                namespace=namespace,
            )

    def disable_scheduler(self, name: str, namespace: str) -> None:
        """
        if scheduler label is missing, has been deleted or namespace
        has been created without label -> suspend cronjob even if it
        doesn't exist

        :param name: str cronjob name
        :param namespace: str kubernetes namespace

        :return None
        """
        self.suspend_cronjob(name=name, namespace=namespace)
        logger.info(
            f"Cronjob {name} has been successfully suspended in {namespace} namespace"
        )

    def enable_scheduler(self, name: str, namespace: str, **kwargs) -> None:
        """
        if scheduler label has been enabled -> find cronjob if exists ->
        if it doesn't -> create cronjob
        if it exists -> patch to unsuspend

        :param name: str cronjob name
        :param namespace: str kubernetes namespace
        :param **kwargs: dict of additional parameters for cronjob template

        :return None
        """
        cron_job = self.cron_job(namespaces=[namespace])

        if cron_job["cronjobs"][namespace]:
            self.unsuspend_cronjob(name=name, namespace=namespace)
            logger.info(
                f"Cronjob {name} has been successfully unsuspended in {namespace} namespace"
            )
            return

        template = Template(cronjob_template)
        body = load(
            template.render(name=name, namespace=namespace, **kwargs),
            Loader=SafeLoader,
        )
        self.create_cronjob(namespace=namespace, body=body)
        logger.info(
            f"Cronjob {name} has been successfully created in {namespace} namespace"
        )
