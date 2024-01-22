from typing import Union, Protocol, Any


class AwsProtocol(Protocol):
    def start_stop_instances(self, payload: Any, replicas: int, namespaces: list[str]):
        pass

    def start_instances(self, instances_ids: Union[str, list[str]]):
        pass

    def stop_instances(self, instances_ids: Union[str, list[str]]):
        pass
