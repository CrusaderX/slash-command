from typing import Union, Any
from itertools import chain
from json import loads
from aioboto3 import Session
from asyncio import gather

from ..models.scaler_model import StatusEnums
from ..models.scaler_model import Resource
from ..protocols.aws_protocol import AwsProtocol
from ..handlers.validation_handler import ScalerDynamodbMissingDataError
from ..config import settings
from ..common.utils import logger

session = Session()


class AwsService:
    @staticmethod
    async def start_stop_instances(
        replicas: int, namespaces: list[str], header: str
    ) -> None:
        # assume that if header is not None, it's a user request from slack
        if header:
            (ns,) = namespaces
            if ns in settings.namespaces_without_deps:
                logger.info(
                    f"Skipping start/stop ec2/rds instances, because namespace doesn't have external dependencies"
                )
                return

        payload = await Fetcher.describe_fetchers(["EC2", "RDS"])
        tasks = list()
        ec2: AwsProtocol = EC2Resource()
        rds: AwsProtocol = RDSResource()

        tasks.append(
            ec2.start_stop_instances(
                payload=payload.get("EC2"),
                replicas=replicas,
                namespaces=namespaces,
            )
        )
        tasks.append(
            rds.start_stop_instances(
                payload=payload.get("RDS"),
                replicas=replicas,
                namespaces=namespaces,
            )
        )

        # don't handle any return values for now
        await gather(*tasks)


class Fetcher:
    @staticmethod
    async def describe_fetchers(
        fetcher_ids: list[str],
    ) -> dict[str, Any]:
        tasks = list()
        result = dict()

        async with session.resource(
            "dynamodb", region_name=settings.aws_region
        ) as dynamodb_resource:
            table = await dynamodb_resource.Table(settings.cacher_state_table)

            for fetcher_id in fetcher_ids:
                tasks.append(table.get_item(Key={"fetcherid": fetcher_id}))

            for task in await gather(*tasks):
                result.update({task["Item"]["fetcherid"]: task["Item"]["data"]})

        return result

    @staticmethod
    def describe_fetcher_instances(namespaces: list[str], payload: Resource):
        resource = Resource(payload=payload)

        for namespace in namespaces:
            for ns in resource.payload:
                if ns.name == namespace:
                    yield ns.ids


class EC2Resource:
    async def start_instances(
        self, instances_ids: Union[str, list[str]]
    ) -> dict[str, list]:
        async with session.resource("ec2", region_name=settings.aws_region) as ec2:
            return (
                await ec2.instances.filter(InstanceIds=instances_ids).start()
            ).pop()["StartingInstances"]

    async def stop_instances(
        self, instances_ids: Union[str, list[str]]
    ) -> dict[str, list]:
        async with session.resource("ec2", region_name=settings.aws_region) as ec2:
            return (await ec2.instances.filter(InstanceIds=instances_ids).stop()).pop()[
                "StoppingInstances"
            ]

    async def start_stop_instances(
        self, payload: Any, replicas: int, namespaces: list[str]
    ) -> Union[str, dict[str, list]]:
        if not payload:
            ScalerDynamodbMissingDataError(fetcher_id="EC2")

        instances_ids = list(
            chain.from_iterable(
                Fetcher.describe_fetcher_instances(
                    namespaces=namespaces, payload=loads(payload)
                )
            )
        )

        if not instances_ids:
            return StatusEnums.NOT_FOUND

        if replicas > 0:
            return await self.start_instances(instances_ids=instances_ids)

        return await self.stop_instances(instances_ids=instances_ids)


class RDSResource:
    async def start_instances(self, db_instance_identifier: str) -> dict[str, str]:
        async with session.client("rds", region_name=settings.aws_region) as rds:
            try:
                return {
                    db_instance_identifier: (
                        await rds.start_db_instance(
                            DBInstanceIdentifier=db_instance_identifier
                        )
                    )["DBInstance"]["DBInstanceStatus"]
                }
            except Exception as error:
                return {db_instance_identifier: f"{error}"}

    async def stop_instances(self, db_instance_identifier: str) -> dict[str, str]:
        async with session.client("rds", region_name=settings.aws_region) as rds:
            try:
                return {
                    db_instance_identifier: (
                        await rds.stop_db_instance(
                            DBInstanceIdentifier=db_instance_identifier
                        )
                    )["DBInstance"]["DBInstanceStatus"]
                }
            except Exception as error:
                return {db_instance_identifier: f"{error}"}

    async def start_stop_instances(
        self, payload: Any, replicas: int, namespaces: list[str]
    ) -> Union[str, dict[str, list]]:
        if not payload:
            ScalerDynamodbMissingDataError(fetcher_id="RDS")

        db_instance_identifiers = list(
            chain.from_iterable(
                Fetcher.describe_fetcher_instances(
                    namespaces=namespaces, payload=loads(payload)
                )
            )
        )

        if not db_instance_identifiers:
            return StatusEnums.NOT_FOUND

        response = dict()
        tasks = list()

        for db_instance_identifier in db_instance_identifiers:
            if replicas > 0:
                tasks.append(
                    self.start_instances(db_instance_identifier=db_instance_identifier)
                )
                continue
            tasks.append(
                self.stop_instances(db_instance_identifier=db_instance_identifier)
            )

        for task in await gather(*tasks):
            response.update(task)

        return response
