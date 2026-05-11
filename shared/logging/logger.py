import json
import logging
import sys
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stdout
)


logger = logging.getLogger("commerce-platform")


def log_event(
    service: str,
    event: str,
    status: str = "success",
    trace_id: str = "unknown",
    **kwargs
):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service,
        "event": event,
        "status": status,
        "trace_id": trace_id,
        **kwargs
    }

    logger.info(json.dumps(payload))