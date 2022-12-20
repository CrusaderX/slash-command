from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    namespace_label: str = "scheduler"
    default_app_web_label = "app-web"
    cron_job_default_label: str = "dev-scaler"
    cron_job_default_schedule_time: str = "0 17 * * 1-5"
    namespaces: List[str] = [
        "dev1",
        "dev2",
        "dev3"
    ]


settings = Settings()
