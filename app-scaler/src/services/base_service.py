from http import HTTPStatus
from kubernetes import client, config
from collections import ChainMap
from typing import Dict, List, Optional, Generator, Union

from ..models.scaler_model import PayloadFiledsEnums, KindsEnums
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
        kind: str,
        namespaces: List[str],
        label_selector: Optional[str],
        obj: Optional[object] = apps_v1,
        payload_key: Optional[PayloadFiledsEnums] = PayloadFiledsEnums.DEPLOYMENT,
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
                result = getattr(obj, f"list_namespaced_{kind}")(
                    namespace=namespace, label_selector=label_selector
                ).to_dict()
            except Exception as error:
                raise ScalerInternalError(error=error, status_code=error.status)

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
                        kind="deployment",
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
                        kind="stateful_set",
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
                        kind="cron_job",
                        namespaces=namespaces,
                        label_selector=label_selector,
                        payload_key=PayloadFiledsEnums.CRON_JOB,
                        obj=batch_v1,
                    )
                )
            )
        }

    @staticmethod
    def kind_status(
        kind: str,
        namespace: str,
        name: str,
    ) -> dict:
        try:
            return getattr(apps_v1, f"read_namespaced_{kind}")(
                name=name,
                namespace=namespace,
            )
        except Exception as error:
            if error.status != 404:
                raise ScalerInternalError(error=error, status_code=error.status)

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
        except Exception as error:
            if error.status != HTTPStatus.NOT_FOUND:
                raise ScalerInternalError(error=error, status_code=error.status)

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

    def create_cronjob(self, namespace: str, body: Dict) -> None:
        try:
            batch_v1.create_namespaced_cron_job(
                namespace=namespace,
                body=body,
            )
        except Exception as error:
            if error.status != HTTPStatus.CONFLICT:
                logger.error(f"An kubernetes error occured: {error.body}")
                raise ScalerInternalError(error=error, status_code=error.status)

    def suspend_cronjob(self, name: str, namespace: str) -> None:
        return self.patch_cronjobs(
            name=name, namespace=namespace, body={"spec": {"suspend": True}}
        )

    def unsuspend_cronjob(self, name: str, namespace: str) -> None:
        return self.patch_cronjobs(
            name=name, namespace=namespace, body={"spec": {"suspend": False}}
        )
