from prometheus_client import Counter
from prometheus_client import Histogram


EVENTS_PROCESSED = Counter(
    "events_processed_total",
    "Total processed events",
    ["service", "event"]
)

EVENTS_FAILED = Counter(
    "events_failed_total",
    "Total failed events",
    ["service", "event"]
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["service", "endpoint"]
)