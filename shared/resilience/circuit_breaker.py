import logging

import pybreaker

logger = logging.getLogger(__name__)


class CircuitBreakerListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        logger.warning(
            f"[CircuitBreaker] {cb.name}: "
            f"{old_state.name} -> {new_state.name}"
        )

    def failure(self, cb, exc):
        logger.error(
            f"[CircuitBreaker] {cb.name}: failure detected -> {exc}"
        )

    def success(self, cb):
        logger.info(
            f"[CircuitBreaker] {cb.name}: successful call"
        )


payment_breaker = pybreaker.CircuitBreaker(
    name="payment-service",
    fail_max=5,
    reset_timeout=60,
    listeners=[CircuitBreakerListener()]
)

inventory_breaker = pybreaker.CircuitBreaker(
    name="inventory-service",
    fail_max=5,
    reset_timeout=60,
    listeners=[CircuitBreakerListener()]
)

notification_breaker = pybreaker.CircuitBreaker(
    name="notification-service",
    fail_max=5,
    reset_timeout=60,
    listeners=[CircuitBreakerListener()]
)

order_breaker = pybreaker.CircuitBreaker(
    name="order-service",
    fail_max=5,
    reset_timeout=60,
    listeners=[CircuitBreakerListener()]
)