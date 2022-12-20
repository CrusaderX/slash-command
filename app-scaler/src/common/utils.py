from logging import (
    getLogger,
    INFO,
    Formatter,
    StreamHandler,
)

logger = getLogger()
logger.setLevel(INFO)
formatter = Formatter(
    "{'time':'%(asctime)s', 'name': '%(name)s', 'level': '%(levelname)s', 'message': '%(message)s'}"
)
logHandler = StreamHandler()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
