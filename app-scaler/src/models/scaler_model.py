from pydantic import BaseModel, conint
from typing import Optional, List
from enum import Enum
from ..config import settings


class KindsEnums(str, Enum):
    DEPLOYMENT = "deployment"
    STATEFUL_SET = "stateful_set"
    CRON_JOB = "cron_job"


class PayloadFiledsEnums(str, Enum):
    DEPLOYMENT = "replicas"
    STATEFUL_SET = "replicas"
    CRON_JOB = "schedule"


class StatusEnums(str, Enum):
    NOT_FOUND = "kind not found"
    STOPPED = "stopped"
    PENDING = "pending"
    RUNNING = "running"


class ScalerModel(BaseModel):
    namespaces: List[str]
    kinds: List[KindsEnums] = [KindsEnums.DEPLOYMENT, KindsEnums.STATEFUL_SET]
    replicas: Optional[conint(ge=0, le=1)] = 0
    exclude: Optional[List[str]] = []


class ScalerResponseModel(BaseModel):
    namespaces: List[str]
    kinds: List[KindsEnums]
    replicas: Optional[conint(ge=0, le=1)] = 0
    exclude: Optional[List[str]] = []


class ScalerProlongateModel(BaseModel):
    kind: Optional[KindsEnums] = KindsEnums.CRON_JOB
    namespace: str
    hours: Optional[conint(ge=0, le=10)] = 1
    label_selector: Optional[str] = f"app={settings.cron_job_default_label}"


class ScalerProlongateResponseModel(BaseModel):
    namespace: str
    hours: Optional[conint(ge=0, le=10)] = 1


class ScalerScheduleResetModel(BaseModel):
    kind: Optional[KindsEnums] = KindsEnums.CRON_JOB
    namespaces: Optional[List[str]] = settings.namespaces
    label_selector: Optional[str] = f"app={settings.cron_job_default_label}"
    schedule: Optional[str] = settings.cron_job_default_schedule_time


class ScalerScheduleResetResponseModel(BaseModel):
    namespaces: Optional[List[str]] = settings.namespaces
    label_selector: Optional[str] = f"app={settings.cron_job_default_label}"
    schedule: Optional[str] = settings.cron_job_default_schedule_time


class ScalerStatusModel(BaseModel):
    kind: Optional[KindsEnums] = KindsEnums.DEPLOYMENT
    namespace: str
    label_selector: Optional[str] = settings.default_app_web_label
