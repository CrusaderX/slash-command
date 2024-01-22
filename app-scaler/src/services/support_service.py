from jinja2 import Template
from yaml import load, SafeLoader

from ..services.base_service import BaseComponents
from ..models.scaler_model import SupportEnums
from ..handlers.error_handler import (
    ScalerSupportJobExistsError,
    ScalerSupportJobDoesntExistError,
)
from ..templates.job import job_template
from ..common.utils import logger


class SupportService(BaseComponents):
    @staticmethod
    def validate(name: str, job: dict, action: SupportEnums, namespace: str) -> None:
        if action == SupportEnums.START and job.get("jobs", {}).get(namespace, {}):
            raise ScalerSupportJobExistsError(uid=name)

        if action == SupportEnums.STOP and not job.get("jobs", {}).get(namespace, {}):
            raise ScalerSupportJobDoesntExistError(uid=name)

    def create_or_delete(
        self, namespace: str, action: SupportEnums, name: str, size: str
    ) -> None:
        if action == SupportEnums.START:
            self.create(name=name, namespace=namespace, size=size)

        if action == SupportEnums.STOP:
            self.delete(name=name, namespace=namespace)

    def delete(self, name: str, namespace: str) -> None:
        self.delete_job(name=name, namespace=namespace)
        logger.info(
            f"Job {name} has been successfully deleted in {namespace} namespace"
        )

    def create(self, name: str, namespace: str, **kwargs) -> None:
        template = Template(job_template)
        body = load(
            template.render(name=name, namespace=namespace, **kwargs),
            Loader=SafeLoader,
        )
        self.create_job(namespace=namespace, body=body)
        logger.info(
            f"Job {name} has been successfully created in {namespace} namespace"
        )
