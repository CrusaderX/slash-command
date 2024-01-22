from http import HTTPStatus

from .errors import SlackBotError


class DevenvActionIsNotImplementedError(SlackBotError):
    def __init__(self, action: str):
        status_code = HTTPStatus.OK
        detail = f"Bad action {action}, see help message for slash command"

        super().__init__(status_code=status_code, detail=detail)


class DevenvArgumentListTooBigError(SlackBotError):
    def __init__(self, text: str):
        status_code = HTTPStatus.OK
        detail = f"""
            Argument list is too long {text}, please, follow the current pattern: /devenv <stop/start/prolongate> <namespace> [for <Nh>].
            For instance: 
                /devenv prolongate dev1 for 1h  
                /devenv start dev2
        """

        super().__init__(status_code=status_code, detail=detail)


class DevenvNamespaceIsNotAllowedError(SlackBotError):
    def __init__(self, namespace: str):
        status_code = HTTPStatus.OK
        detail = f"Provided namespace {namespace} is not allowed"

        super().__init__(status_code=status_code, detail=detail)


class DevenvInvalidTokenError(SlackBotError):
    def __init__(self):
        status_code = HTTPStatus.OK
        detail = f"Invalid token"

        super().__init__(status_code=status_code, detail=detail)


class DevenvInvalidRequestError(SlackBotError):
    def __init__(self):
        status_code = HTTPStatus.OK
        detail = f"Invalid request"

        super().__init__(status_code=status_code, detail=detail)


class DevenvProlongateWrongTimeError(SlackBotError):
    def __init__(self, hours: int):
        status_code = HTTPStatus.OK
        detail = f"Provided time {hours} cannot be negative, zero or greater than 24"

        super().__init__(status_code=status_code, detail=detail)


class DevenvSupportSizeError(SlackBotError):
    def __init__(self, size: str):
        status_code = HTTPStatus.OK
        detail = {"status": "error", "message": f"Provided size {size} is incorrect"}

        super().__init__(status_code=status_code, detail=detail)


class ScalerEndpointUnhealthyError(SlackBotError):
    def __init__(self, scaler_status_code: int, scaler_status_test: str):
        status_code = HTTPStatus.OK
        detail = (
            f"error code: {scaler_status_code}, error message: {scaler_status_test}"
        )

        super().__init__(status_code=status_code, detail=detail)
