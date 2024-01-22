from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    aws_region: str = "eu-north-1"
    namespace_label: str = "scheduler"
    default_app_web_label = "app-web"
    cacher_state_table: str = "cacher_actual_state"
    cron_job_default_label: str = "dev-scaler"
    cron_job_default_schedule_time: str = "0 17 * * 1-5"
    namespaces: List[str] = [
        "dev1",
        "dev2",
        ]
    namespaces_without_deps: List[str] = [
        "dev3",
        ]


settings = Settings()
