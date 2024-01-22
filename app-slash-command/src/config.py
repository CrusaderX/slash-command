from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    namespaces: List[str] = [
        "dev1",
        "dev2",
    ]
    namespaces_with_depth: List[str] = [
        "dev3",
    ]
    namespace_prefix: str = ""
    pattern: str = "h|hour|hours"
    scaler_url: str = "http://app-scaler/api/v1"
    secret: str
    slack_bot_token: str
    slack_bot_channel_id: str
    aws_region: str = "eu-north-1"
    dynamodb_table_name: str = "scheduler"
    scheduler_shutdown_time: List[int] = [17, 0]
    scheduler_notifications_minutes_before_shutdown: List[int] = [15, 30, 60]


settings = Settings()
