from boto3 import resource
from botocore import exceptions

from ..config import settings


class DynamoDBService:
    def __init__(self) -> None:
        self._dynamodb = resource("dynamodb", region_name=settings.aws_region)
        self._table = self._dynamodb.Table(settings.dynamodb_table_name)

        try:
            self._dynamodb.create_table(
                TableName=settings.dynamodb_table_name,
                KeySchema=[
                    {"AttributeName": "type", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "type", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            )
        except exceptions.ClientError as error:
            if error.response["Error"]["Code"] != "ResourceInUseException":
                raise

    def dynamodb_put_item(self, item: dict) -> None:
        self._table.put_item(Item=item, TableName=settings.dynamodb_table_name)

    def dynamodb_get_item(self, key: dict) -> dict:
        return self._table.get_item(Key=key)

    def dynamodb_update_item(
        self,
        key: dict,
        update_expression: str,
        expression_attribute_names: dict,
        expression_attribute_values: dict,
    ) -> None:
        self._table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
        )
