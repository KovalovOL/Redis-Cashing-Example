import logging
import sys
from structlog import wrap_logger, processors
from .log_context import add_contextvars


logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO
)

logger = wrap_logger(
    logging.getLogger("app"),
    processors=[
        processors.TimeStamper(fmt="iso"),
        processors.add_log_level,
        add_contextvars,
        processors.StackInfoRenderer(),
        processors.format_exc_info,
        processors.CallsiteParameterAdder([
                processors.CallsiteParameter.FILENAME,
                processors.CallsiteParameter.FUNC_NAME
            ]
        ),
        processors.JSONRenderer()
    ]
)