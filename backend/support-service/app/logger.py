import json
import datetime


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

    print(json.dumps(log), flush=True)