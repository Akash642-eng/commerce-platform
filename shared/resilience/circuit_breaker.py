import pybreaker

payment_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)