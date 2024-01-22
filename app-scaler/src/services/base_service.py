from http import HTTPStatus
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from collections import ChainMap
from typing import Dict, List, Optional, Generator, Union, Any

from ..models.scaler_model import KindsEnums, PayloadFieldsEnums
from ..handlers.error_handler import ScalerInternalError
from ..common.utils import logger

try:
    config.load_incluster_config()
except config.ConfigException:
    try:
        config.load_kube_config()
    except config.ConfigException:
        raise Exception("Could not configure kubernetes python client")

apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()
batch_v1 = client.BatchV1Api()


class BaseComponents:
    @staticmethod
    def _grabber(
        kind: KindsEnums,
        namespaces: List[str],
        label_selector: Optional[str],
        obj: Optional[object] = apps_v1,
        payload_key: Optional[PayloadFieldsEnums] = PayloadFieldsEnums.DEPLOYMENT,
    ) -> Generator[Dict, None, None]:
        """
        Result will always has 'items' and we should iterate over it

        :param kind: str
        :param namespaces: List[str]
        :param label_selector: Optional[str]
        :param obj: Optional[object]

        :return Generator[List, None, None]
        """
        for namespace in namespaces:
            try:
                result = getattr(obj, f"list_namespaced_{kind.value}")(
                    namespace=namespace, label_selector=label_selector
                ).to_dict()
            except ApiException as error:
                raise ScalerInternalError(error=error.reason, status_code=error.status)

            kinds = {}
            kinds[namespace] = {}

            for current in result["items"]:
                kinds[namespace] = {
                    current["metadata"]["name"]: current["spec"][payload_key],
                    **kinds[namespace],
                }
            yield kinds

    def deployment(
        self, namespaces: List[str], label_selector: Optional[str] = None
    ) -> Dict:
        """
        Get existing deployments across provided namespaces

        :param namespaces: List[str]
        :param label_selector: Optional[str]

        :return Dict
        """
        return {
            "deployments": dict(
                ChainMap(
                    *self._grabber(
                        kind=KindsEnums.DEPLOYMENT,
                        namespaces=namespaces,
                        label_selector=label_selector,
                    )
                )
            )
        }

    def stateful_set(
        self, namespaces: List[str], label_selector: Optional[str] = None
    ) -> Dict:
        """
        Get existing statefulsets across provided namespaces

        :param namespaces: List[str]
        :param label_selector: Optional[str]

        :return Dict
        """
        return {
            "statefulsets": dict(
                ChainMap(
                    *self._grabber(
                        kind=KindsEnums.STATEFUL_SET,
                        namespaces=namespaces,
                        label_selector=label_selector,
                    )
                )
            )
        }

    def cron_job(
        self,
        namespaces: List[str],
        label_selector: Optional[str] = "app=dev-scaler",
    ) -> Dict:
        """
        Get existing cronjob in provided namespace

        :param namespaces: List[str]
        :param label_selector: Optional[str]

        :return Dict
        """
        return {
            "cronjobs": dict(
                ChainMap(
                    *self._grabber(
                        kind=KindsEnums.CRON_JOB,
                        namespaces=namespaces,
                        label_selector=label_selector,
                        payload_key=PayloadFieldsEnums.CRON_JOB,
                        obj=batch_v1,
                    )
                )
            )
        }

    def job(
        self,
        namespaces: List[str],
        label_selector: str | None = None,
    ) -> Dict:
        """
        Get existing job in provided namespace

        :param namespaces: List[str]
        :param label_selector: Optional[str]

        :return Dict
        """
        return {
            "jobs": dict(
                ChainMap(
                    *self._grabber(
                        kind=KindsEnums.JOB,
                        namespaces=namespaces,
                        label_selector=label_selector,
                        payload_key=PayloadFieldsEnums.JOB,
                        obj=batch_v1,
                    )
                )
            )
        }

    @staticmethod
    def _delete(
        kind: KindsEnums,
        name: str,
        namespace: str,
        obj: Optional[object] = apps_v1,
    ) -> None:
        """
        Delete kind

        :param kind: str
        :param name: str
        :param namespace: str
        :param obj: Optional[object]

        :return Any
        """
        try:
            getattr(obj, f"delete_namespaced_{kind.value}")(
                name=name,
                namespace=namespace,
                propagation_policy="Background",
            )
        except ApiException as error:
            raise ScalerInternalError(error=error.reason, status_code=error.status)

    def delete_job(
        self,
        name: str,
        namespace: str,
    ) -> None:
        """
        Delete job

        :param name: str
        :param namespace: str

        :return None
        """
        self._delete(kind=KindsEnums.JOB, name=name, namespace=namespace, obj=batch_v1)

    @staticmethod
    def kind_status(
        kind: KindsEnums,
        namespace: str,
        name: str,
    ) -> Any:
        try:
            return getattr(apps_v1, f"read_namespaced_{kind.value}")(
                name=name,
                namespace=namespace,
            )
        except ApiException as error:
            if error.status != 404:
                raise ScalerInternalError(error=error.reason, status_code=error.status)

    @staticmethod
    def _patch(
        kind: str,
        name: str,
        namespace: str,
        body: Dict,
        obj: Optional[object] = apps_v1,
    ) -> Union[Exception, None]:
        """
        Trying to patch *kind (could be KindsEnum) with required body

        :param kind: str
        :param name: Optional[str]
        :param namespaces: List[str]
        :param body: Dict
        :param obj: Optional[object]

        :return None
        """
        try:
            getattr(obj, f"patch_namespaced_{kind}")(
                name=name,
                namespace=namespace,
                body=body,
            )
        except ApiException as error:
            if error.status != HTTPStatus.NOT_FOUND:
                raise ScalerInternalError(error=error.reason, status_code=error.status)

    def patch_deployments(
        self,
        name: str,
        namespace: str,
        body: dict,
    ) -> None:
        """
        Patch existing deployment to provided replica count

        :param name: str
        :param namespaces: List[str]
        :param body: Dict

        :return None
        """
        self._patch(kind="deployment_scale", name=name, namespace=namespace, body=body)

    def patch_statefulsets(self, name: str, namespace: str, body: Dict):
        """
        Patch existing statefulset to required replica count

        :param name: str
        :param namespaces: List[str]
        :param body: dict

        :return None
        """
        self._patch(
            kind="stateful_set_scale", name=name, namespace=namespace, body=body
        )

    def patch_cronjobs(self, name: str, namespace: str, body: Dict) -> None:
        """
        Patch existing cron_job with required schedule window

        :param namespaces: List[str]
        :param body: Dict
        :param name: str

        :return None
        """
        self._patch(
            kind="cron_job", name=name, namespace=namespace, body=body, obj=batch_v1
        )

    def create_job(self, namespace: str, body: Dict) -> None:
        try:
            batch_v1.create_namespaced_job(
                namespace=namespace,
                body=body,
            )
        except ApiException as error:
            raise ScalerInternalError(error=error.reason, status_code=error.status)

    def create_cronjob(self, namespace: str, body: Dict) -> None:
        try:
            batch_v1.create_namespaced_cron_job(
                namespace=namespace,
                body=body,
            )
        except ApiException as error:
            if error.status != HTTPStatus.CONFLICT:
                logger.error(f"An kubernetes error occured: {error.body}")
                raise ScalerInternalError(error=error.reason, status_code=error.status)

    def suspend_cronjob(self, name: str, namespace: str) -> None:
        return self.patch_cronjobs(
            name=name, namespace=namespace, body={"spec": {"suspend": True}}
        )

    def unsuspend_cronjob(self, name: str, namespace: str) -> None:
        return self.patch_cronjobs(
            name=name, namespace=namespace, body={"spec": {"suspend": False}}
        )
