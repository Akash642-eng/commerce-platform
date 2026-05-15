from prometheus_client import Counter

EVENTS_PROCESSED = Counter(
    "inventory_events_processed_total",
    "Total processed inventory events",
    ["service", "event"],
)

EVENTS_FAILED = Counter(
    "inventory_events_failed_total",
    "Total failed inventory events",
    ["service", "event"],
)
