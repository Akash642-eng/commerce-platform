import json
from datetime import datetime, timezone


def log_event(
    service: str,
    event: str,
    trace_id: str = "unknown",
    message: str = "",
    data: dict = None,
    level: str = "INFO",
):

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service,
        "event": event,
        "trace_id": trace_id,
        "level": level.upper(),
        "message": message,
        "data": data or {},
    }

    print(json.dumps(payload), flush=True)
