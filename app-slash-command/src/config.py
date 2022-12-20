from pydantic import BaseSettings
from typing import List

# every setting can be setup via environment variable,
# foe instance: export SLACK_BOT_TOKEN=x-bottokenexample

class Settings(BaseSettings):
    namespaces: List[str] = [
        "dev1",
        "dev2",
        "dev3"
    ]
    pattern: str = "h|hour|hours"
    scaler_url: str = "http://app-scaler.default.svc.cluster.local/api/v1"
    secret: str
    slack_bot_token: str
    slack_bot_channel_id: str
    aws_secret_access_key: str
    aws_access_key_id: str
    aws_region: str = "us-east-1"
    dynamodb_table_name: str = "scheduler"
    scheduler_shutdown_time: List[int] = [17, 0]
    scheduler_notifications_minutes_before_shutdown: List[int] = [15, 30, 60]


settings = Settings()
