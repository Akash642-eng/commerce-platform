import httpx

DEFAULT_TIMEOUT = httpx.Timeout(
    connect=5.0,
    read=10.0,
    write=5.0,
    pool=5.0
)

FAST_TIMEOUT = httpx.Timeout(
    connect=2.0,
    read=3.0,
    write=2.0,
    pool=2.0
)

SLOW_TIMEOUT = httpx.Timeout(
    connect=10.0,
    read=30.0,
    write=10.0,
    pool=10.0
)