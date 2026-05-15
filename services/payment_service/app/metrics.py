from prometheus_client import Counter

EVENTS_PROCESSED = Counter(
    "payment_events_processed_total",
    "Total processed payment events",
    ["service", "event"],
)

EVENTS_FAILED = Counter(
    "payment_events_failed_total", "Total failed payment events", ["service", "event"]
)
