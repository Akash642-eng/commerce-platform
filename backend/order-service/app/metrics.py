from prometheus_client import Counter, Histogram

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

RETRY_EVENTS = Counter(
    "retry_events_total",
    "Total retry events",
    ["service"]
)

DLQ_EVENTS = Counter(
    "dlq_events_total",
    "Total DLQ events",
    ["service"]
)

PROCESSING_TIME = Histogram(
    "event_processing_seconds",
    "Event processing latency",
    ["service", "event"]
)