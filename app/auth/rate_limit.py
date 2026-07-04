import logging
import time
from collections import defaultdict, deque

from auth.errors import TooManyLoginAttemptsError

logger = logging.getLogger(__name__)


class LoginRateLimiter:
    """In-memory limiter for failed login attempts, keyed by client ip + username.

    Good enough for a single-process deployment; state is lost on restart.
    """

    def __init__(self, max_failures: int = 5, window_seconds: int = 15 * 60):
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._failures: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        failures = self._prune(key)
        if not failures:
            self._failures.pop(key, None)
            return
        if len(failures) >= self.max_failures:
            logger.warning("login rate limit hit for %s", key)
            raise TooManyLoginAttemptsError

    def record_failure(self, key: str) -> None:
        self._prune(key).append(time.monotonic())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)

    def _prune(self, key: str) -> deque[float]:
        failures = self._failures[key]
        cutoff = time.monotonic() - self.window_seconds
        while failures and failures[0] < cutoff:
            failures.popleft()
        return failures
