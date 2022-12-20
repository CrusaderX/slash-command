from pydantic import BaseModel
from typing import Optional, Union
from enum import Enum


class OperationEnums(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"


class LabelEnums(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class StatusModel(BaseModel):
    code: Optional[int] = 200
    message: Optional[str] = None


class ResponseModel(BaseModel):
    uid: str
    allowed: Optional[bool] = True
    status: Union[StatusModel, None] = None


class AdmissionWebhookResponseModel(BaseModel):
    apiVersion: str = "admission.k8s.io/v1"
    kind: str = "AdmissionReview"
    response: ResponseModel
