from prometheus_client import Counter, Histogram, Gauge


# HTTP METRICS

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["service", "endpoint"]
)


# GENERIC EVENT METRICS

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

# RETRY / DLQ METRICS


RETRY_COUNT = Counter(
    "retry_total",
    "Total retry attempts",
    ["service", "event"]
)

DLQ_COUNT = Counter(
    "dlq_total",
    "Total dead-letter queue events",
    ["service", "event"]
)


# SAGA METRICS

SAGA_SUCCESS = Counter(
    "saga_success_total",
    "Total successful saga executions",
    ["service", "saga"]
)

SAGA_FAILURE = Counter(
    "saga_failure_total",
    "Total failed saga executions",
    ["service", "saga"]
)


# CONSUMER METRICS

CONSUMER_ACTIVE = Gauge(
    "consumer_active",
    "Current active consumers",
    ["service", "consumer"]
)

CONSUMER_LAG = Gauge(
    "consumer_lag",
    "Current consumer lag",
    ["service", "queue"]
)


# PAYMENT METRICS

PAYMENT_SUCCESS = Counter(
    "payment_success_total",
    "Total successful payments",
    ["service"]
)

PAYMENT_FAILURE = Counter(
    "payment_failure_total",
    "Total failed payments",
    ["service"]
)


# INVENTORY METRICS

INVENTORY_RESERVED = Counter(
    "inventory_reserved_total",
    "Total inventory reservations",
    ["service"]
)

INVENTORY_RELEASED = Counter(
    "inventory_released_total",
    "Total inventory releases",
    ["service"]
)

LOW_STOCK_ALERT = Counter(
    "low_stock_alert_total",
    "Total low stock alerts",
    ["service", "product"]
)


# ORDER METRICS

ORDERS_CREATED = Counter(
    "orders_created_total",
    "Total created orders",
    ["service"]
)

ORDERS_FAILED = Counter(
    "orders_failed_total",
    "Total failed orders",
    ["service"]
)

ORDERS_COMPLETED = Counter(
    "orders_completed_total",
    "Total completed orders",
    ["service"]
)

ORDERS_CANCELLED = Counter(
    "orders_cancelled_total",
    "Total cancelled orders",
    ["service"]
)


# AUTH METRICS

JWT_CREATED = Counter(
    "jwt_created_total",
    "Total JWT tokens created",
    ["service"]
)

JWT_VALIDATED = Counter(
    "jwt_validated_total",
    "Total JWT validations",
    ["service"]
)

JWT_FAILED = Counter(
    "jwt_failed_total",
    "Total failed JWT validations",
    ["service"]
)

AUTH_LOGIN_SUCCESS = Counter(
    "auth_login_success_total",
    "Total successful logins",
    ["service"]
)

AUTH_LOGIN_FAILED = Counter(
    "auth_login_failed_total",
    "Total failed logins",
    ["service"]
)



# CACHE METRICS

CACHE_HIT = Counter(
    "cache_hit_total",
    "Total cache hits",
    ["service"]
)

CACHE_MISS = Counter(
    "cache_miss_total",
    "Total cache misses",
    ["service"]
)


# DATABASE METRICS

DB_QUERY_COUNT = Counter(
    "db_query_total",
    "Total database queries",
    ["service"]
)

DB_QUERY_FAILURE = Counter(
    "db_query_failure_total",
    "Total failed database queries",
    ["service"]
)

DB_QUERY_LATENCY = Histogram(
    "db_query_latency_seconds",
    "Database query latency in seconds",
    ["service"]
)

DB_CONNECTION_FAILURE = Counter(
    "db_connection_failure_total",
    "Total database connection failures",
    ["service"]
)


# RABBITMQ 

RABBITMQ_PUBLISHED = Counter(
    "rabbitmq_published_total",
    "Total published RabbitMQ messages",
    ["service", "queue"]
)

RABBITMQ_CONSUMED = Counter(
    "rabbitmq_consumed_total",
    "Total consumed RabbitMQ messages",
    ["service", "queue"]
)

RABBITMQ_FAILED = Counter(
    "rabbitmq_failed_total",
    "Total failed RabbitMQ messages",
    ["service", "queue"]
)

RABBITMQ_RETRY = Counter(
    "rabbitmq_retry_total",
    "Total RabbitMQ retries",
    ["service", "queue"]
)

RABBITMQ_DLQ = Counter(
    "rabbitmq_dlq_total",
    "Total RabbitMQ DLQ events",
    ["service", "queue"]
)

TIMEOUT_TOTAL = Histogram(
    "timeout_total",
    "Total timeout events",
    ["service", "operation"]
)

TIMEOUT_DURATION = Histogram(
    "timeout_duration_seconds",
    "TTimeout duration in seconds",
    ["service", "operation"]
)



# API GATEWAY


RATE_LIMIT_TRIGGERED = Counter(
    "rate_limit_triggered_total",
    "Total rate-limit triggers",
    ["service", "endpoint"]
)

GATEWAY_REQUEST_FORWARDED = Counter(
    "gateway_request_forwarded_total",
    "Total forwarded gateway requests",
    ["service", "target_service"]
)



# SYSTEM HEALTH

SERVICE_HEALTH = Gauge(
    "service_health",
    "Current service health",
    ["service"]
)

ACTIVE_USERS = Gauge(
    "active_users",
    "Current active users",
    ["service"]
)

# PLATFORM 

POD_RESTART_COUNT = Counter(
    "pod_restart_total",
    "Total pod restarts",
    ["service"]
)

DEPLOYMENT_REPLICAS = Gauge(
    "deployment_replicas",
    "Current deployment replica count",
    ["service"]
)