from pydantic import BaseModel
from enum import Enum
from ..config import settings


class KindsEnums(str, Enum):
    DEPLOYMENT = "deployment"
    STATEFUL_SET = "stateful_set"
    CRON_JOB = "cron_job"
    JOB = "job"


class SupportEnums(str, Enum):
    START = "start"
    STOP = "stop"


class PayloadFieldsEnums(str, Enum):
    DEPLOYMENT = "replicas"
    STATEFUL_SET = "replicas"
    CRON_JOB = "schedule"
    JOB = "completions"


class StatusEnums(str, Enum):
    NOT_FOUND = "not found"
    STOPPED = "stopped"
    STOPPING = "stopping"
    PENDING = "pending"
    STARTING = "starting"
    RUNNING = "running"
    UNKNOWN = "unknown"
    SKIPPED = "skipped"


class Namespace(BaseModel):
    name: str
    ids: list[str]


class Resource(BaseModel):
    payload: list[Namespace]


class ScalerModel(BaseModel):
    namespaces: list[str]
    kinds: list[KindsEnums] = [KindsEnums.DEPLOYMENT, KindsEnums.STATEFUL_SET]
    replicas: int = 0
    exclude: list[str] = []


class ScalerProlongateModel(BaseModel):
    kind: KindsEnums = KindsEnums.CRON_JOB
    namespace: str
    hours: int = 1
    label_selector: str = f"app={settings.cron_job_default_label}"


class ScalerProlongateResponseModel(BaseModel):
    namespace: str
    hours: int = 1


class ScalerScheduleResetModel(BaseModel):
    kind: KindsEnums = KindsEnums.CRON_JOB
    namespaces: list[str] = settings.namespaces
    label_selector: str = f"app={settings.cron_job_default_label}"
    schedule: str = settings.cron_job_default_schedule_time


class ScalerScheduleResetResponseModel(BaseModel):
    namespaces: list[str] = settings.namespaces
    label_selector: str = f"app={settings.cron_job_default_label}"
    schedule: str = settings.cron_job_default_schedule_time


class ScalerStatusModel(BaseModel):
    kind: KindsEnums = KindsEnums.DEPLOYMENT
    namespace: str
    label_selector: str = settings.default_app_web_label


class ScalerSupportModel(BaseModel):
    kind: KindsEnums = KindsEnums.JOB
    action: SupportEnums
    name: str
    namespace: str = "support"
    size: str
