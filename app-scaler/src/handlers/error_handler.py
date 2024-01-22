from http import HTTPStatus

from .errors import ScalerError


class ScalerCronJobNameHasChangedError(ScalerError):
    def __init__(self, name: str):
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        detail = f"It seems that cronjob name has been changed: {name} from default 'dev-scaler'"

        super().__init__(status_code=status_code, detail=detail)


class ScalerInternalError(ScalerError):
    def __init__(self, error: str, status_code: int):
        detail = f"{error}"

        super().__init__(status_code=status_code, detail=detail)


class ScalerSupportJobExistsError(ScalerError):
    def __init__(self, uid: str):
        status_code = HTTPStatus.CONFLICT
        detail = f"Job with {uid} uid already exists, use another name"

        super().__init__(status_code=status_code, detail=detail)


class ScalerSupportJobDoesntExistError(ScalerError):
    def __init__(self, uid: str):
        status_code = HTTPStatus.NOT_FOUND
        detail = f"Job with {uid} uid doesn't exist, nothing to stop"

        super().__init__(status_code=status_code, detail=detail)
