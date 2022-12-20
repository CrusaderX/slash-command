from fastapi import HTTPException


class Error(Exception):
    pass


class HTTPError(HTTPException, Error):
    pass


class SlackBotError(HTTPError):
    pass
