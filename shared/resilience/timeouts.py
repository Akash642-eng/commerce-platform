import httpx

DEFAULT_TIMEOUT = httpx.Timeout(
    connect=5.0,  # Time to establish a connection
    read=10.0,    # Time to wait for a response after connection is established
    write=5.0,    # Time to wait for a request to be sent
    pool=5.0      # Time to wait for a connection from the pool
)