class ResilienceException(Exception):
    """Base resilience exception."""
    pass


class PaymentServiceException(ResilienceException):
    """Payment service failure."""
    pass


class InventoryServiceException(ResilienceException):
    """Inventory service failure."""
    pass


class NotificationServiceException(ResilienceException):
    """Notification service failure."""
    pass


class OrderServiceException(ResilienceException):
    """Order service failure."""
    pass


class ExternalServiceException(ResilienceException):
    """External dependency failure."""
    pass


class TimeoutException(ResilienceException):
    """Operation timeout."""
    pass


class CircuitBreakerOpenException(ResilienceException):
    """Circuit breaker open."""
    pass


class RetryExhaustedException(ResilienceException):
    """Retries exhausted."""
    pass