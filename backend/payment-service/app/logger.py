import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)


def log_event(service, trace_id, message, data=None, level="INFO"):
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service,
        "level": level,
        "trace_id": trace_id,
        "message": message,
        "data": data or {}
    }

    print(json.dumps(log))