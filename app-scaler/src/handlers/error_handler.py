from http import HTTPStatus

from .errors import ScalerError


class ScalerCronJobNameHasChangedError(ScalerError):
    def __init__(self, name: str):
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        detail = f"It seems that cronjob name has been changed: {name} from default 'dev-scaler'"

        super().__init__(status_code=status_code, detail=detail)


class ScalerInternalError(ScalerError):
    def __init__(self, error: str, status_code: int):
        detail = f"Something went wrong with error: {error}"

        super().__init__(status_code=status_code, detail=detail)
