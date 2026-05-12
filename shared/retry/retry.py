import time


def retry_operation(
    fn,
    retries=3,
    delay=2
):

    last_error = None

    for attempt in range(retries):

        try:

            return fn()

        except Exception as e:

            last_error = e

            time.sleep(delay)

    raise last_error