from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

import logging

logger = logging.getLogger(__name__)


retry_policy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=1,
        min=2,
        max=10
    ),
    retry=retry_if_exception_type(Exception),
    before_sleep=before_sleep_log(
        logger,
        logging.WARNING
    ),
    reraise=True
)