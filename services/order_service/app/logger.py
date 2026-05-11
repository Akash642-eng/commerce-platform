import json
from datetime import datetime, timezone


def log_event(
    service: str,
    trace_id: str,
    message: str,
    data: dict = None,
    level: str = "INFO"
):
    try:
        log = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "service": service,
            "level": level.upper(),
            "trace_id": trace_id or "N/A",
            "message": message,
            "data": data if isinstance(data, dict) else {"value": str(data)}
        }

        print(json.dumps(log, default=str), flush=True)

    except Exception as e:
        
        fallback = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "service": service,
            "level": "ERROR",
            "trace_id": trace_id or "N/A",
            "message": "Logging failure",
            "data": {"error": str(e)}
        }
        print(json.dumps(fallback), flush=True)