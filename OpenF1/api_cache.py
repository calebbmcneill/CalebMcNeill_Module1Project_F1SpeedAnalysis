import requests
import time
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone


_response_cache = {}
_last_request_time = 0.0
MIN_REQUEST_INTERVAL = 0.25
MAX_RETRIES = 5


def _retry_delay(response, attempt):
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            try:
                retry_time = parsedate_to_datetime(retry_after)
                if retry_time.tzinfo is None:
                    retry_time = retry_time.replace(tzinfo=timezone.utc)
                return max(
                    0.0,
                    (retry_time - datetime.now(timezone.utc)).total_seconds(),
                )
            except (TypeError, ValueError, OverflowError):
                pass
    return min(30.0, 2.0**attempt)


def get_cached(url, params=None, timeout=30):
    global _last_request_time

    cache_key = (url, tuple(sorted((params or {}).items())))
    if cache_key in _response_cache:
        return _response_cache[cache_key]

    for attempt in range(MAX_RETRIES + 1):
        elapsed = time.monotonic() - _last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)

        response = requests.get(url, params=params, timeout=timeout)
        _last_request_time = time.monotonic()

        if response.status_code != 429:
            _response_cache[cache_key] = response
            return response

        if attempt == MAX_RETRIES:
            response.raise_for_status()
        time.sleep(_retry_delay(response, attempt))

    raise RuntimeError("Unreachable API retry state")
