import json
import logging
import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)


logger = logging.getLogger("user-service")


def log_event(
    service: str,
    trace_id: str,
    message: str,
    data: dict = None,
    level: str = "INFO"
):

    log = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "service": service,
        "level": level,
        "trace_id": trace_id,
        "message": message,
        "data": data or {}
    }

    log_message = json.dumps(log)

    if level == "ERROR":

        logger.error(log_message)

    elif level == "WARNING":

        logger.warning(log_message)

    else:

        logger.info(log_message)