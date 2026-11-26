import time
import subprocess
from functools import wraps
from rich.console import Console

console = Console()

MAX_ATTEMPTS = 4
RETRY_DELAYS = (2, 4, 8)

TRANSIENT_ERRORS = (
    "server_is_overloaded",
    "service_unavailable",
    "temporarily_unavailable",
    "internal_server_error",
    "bad gateway",
    "gateway timeout",
    "econnreset",
    "econnrefused",
    "etimedout",
    "connection reset",
    "fetch failed",
    "status 502",
    "status 503",
    "status 504",
    "http 502",
    "http 503",
    "http 504",
)

def is_retryable(value):
    if isinstance(value, (
        TimeoutError,
        subprocess.TimeoutExpired,
        ConnectionError
    )):
        return True

    message = str(value).lower()

    return any(
        error in message
        for error in TRANSIENT_ERRORS
    )


def smart_retry(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        for attempt in range(MAX_ATTEMPTS):
            try:
                result = function(*args, **kwargs)

                if not is_retryable(result):
                    return result

                if attempt == MAX_ATTEMPTS - 1:
                    return result

            except Exception as error:
                if not is_retryable(error):
                    raise

                if attempt == MAX_ATTEMPTS - 1:
                    raise

            delay = RETRY_DELAYS[attempt]

            console.print(
                f"[yellow]Temporary backend error. "
                f"Retry {attempt + 2}/{MAX_ATTEMPTS} "
                f"in {delay}s...[/yellow]"
            )

            time.sleep(delay)

    return wrapped
