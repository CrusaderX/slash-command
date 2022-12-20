from datetime import datetime, timedelta
from slack_sdk import WebClient

from ..config import settings
from .dynamodb_service import DynamoDBService

dynamodb = DynamoDBService()
client = WebClient(token=settings.slack_bot_token)


class NotificationService:
    @staticmethod
    def slack_schedule_message(epoch: int, text: str) -> int:
        return client.chat_scheduleMessage(
            channel=settings.slack_bot_channel_id,
            post_at=epoch,
            text=text,
        )["scheduled_message_id"]

    @staticmethod
    def slack_delete_scheduled_message(scheduled_message_id: int) -> None:
        client.chat_deleteScheduledMessage(
            channel=settings.slack_bot_channel_id,
            scheduled_message_id=scheduled_message_id,
        )

    @staticmethod
    def set_default_notifications_slots() -> None:
        """
        type          | notifications                                  | namespaces
        ---           | ---                                            | ---
        global        | [{"epoch": "N", "scheduled_message_id": "N"}]  | []

        We store data for future requests and for now we don't do any useful work with that.
        For every notification trigger before shutdown we have to calculate epoch timestamp
        for slack scheduleMessage method. Calculation based on the default shutdown time minus
        delayed minutes. This function will be triggered every day at morning time to demolish
        prolongated environments notifications along with re-calculated epoch.
        """
        hour, minute = settings.scheduler_shutdown_time
        item: dict = {}

        for minutes in settings.scheduler_notifications_minutes_before_shutdown:
            delta = datetime.now().replace(
                hour=hour, minute=minute, second=0, microsecond=0
            ) - timedelta(minutes=minutes)
            epoch = int(delta.strftime("%s"))
            text = f"Kubernetes namespaces will be stopped in {minutes} minutes, except prolongated"
            scheduled_message_id = NotificationService.slack_schedule_message(
                epoch=epoch, text=text
            )

            item.update(
                {
                    epoch: {
                        "epoch": epoch,
                        "scheduled_message_id": scheduled_message_id,
                    }
                }
            )

        dynamodb.dynamodb_put_item(
            item={
                "type": "global",
                "notifications": [
                    {
                        "epoch": v["epoch"],
                        "scheduled_message_id": v["scheduled_message_id"],
                    }
                    for v in item.values()
                ],
                "namespaces": settings.namespaces,
            }
        )
        dynamodb.dynamodb_put_item(
            item={
                "type": "prolongated",
                "notifications": {},
            }
        )

    @staticmethod
    def update_default_notification_slot(namespace: str, hours: int) -> None:
        """
        type          | notifications
        ---           | ---
        prolongated   | {"namespace": [{"epoch": "N", "text": "S", "scheduled_message_id": "N"}]}

        If namespace already has been prolongated, we have to delete slackSchedule message
        to avoid earliest notifications. Updated epoch will be calculated based on default
        shutdown time plus prolongated hours minus delayed notifications minutes.
        """
        hour, minute = settings.scheduler_shutdown_time
        item: dict = {}

        plorongated_namespaces = dynamodb.dynamodb_get_item(key={"type": "prolongated"})

        if (
            "Item" in plorongated_namespaces
            and namespace in plorongated_namespaces["Item"]["notifications"]
        ):
            for plorongated_namespace in plorongated_namespaces["Item"][
                "notifications"
            ][namespace]:
                scheduled_message_id = plorongated_namespace["scheduled_message_id"]
                NotificationService.slack_delete_scheduled_message(
                    scheduled_message_id=scheduled_message_id
                )

        for minutes in settings.scheduler_notifications_minutes_before_shutdown:
            hours_to_minutes = hours * 60 - minutes
            delta = datetime.now().replace(
                hour=hour, minute=minute, second=0, microsecond=0
            ) + timedelta(minutes=hours_to_minutes)
            epoch = int(delta.strftime("%s"))
            text = f"Environment {namespace} will be stopped in {minutes} minutes"
            scheduled_message_id = NotificationService.slack_schedule_message(
                epoch=epoch, text=text
            )
            item.update(
                {
                    epoch: {
                        "epoch": epoch,
                        "text": text,
                        "scheduled_message_id": scheduled_message_id,
                    }
                }
            )
        dynamodb.dynamodb_update_item(
            key={"type": "prolongated"},
            update_expression="SET #n.#ns = :item",
            expression_attribute_names={
                "#n": "notifications",
                "#ns": namespace,
            },
            expression_attribute_values={
                ":item": [
                    {
                        "epoch": v["epoch"],
                        "text": v["text"],
                        "scheduled_message_id": v["scheduled_message_id"],
                    }
                    for v in item.values()
                ]
            },
        )
