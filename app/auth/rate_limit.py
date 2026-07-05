import logging
import time
from collections import defaultdict, deque

from auth.errors import TooManyLoginAttemptsError

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """In-memory sliding-window limiter.

    Good enough for a single-process deployment; state is lost on restart.
    """

    def __init__(self, max_events: int = 5, window_seconds: int = 15 * 60):
        self.max_events = max_events
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        events = self._prune(key)
        if not events:
            self._events.pop(key, None)
            return
        if len(events) >= self.max_events:
            logger.warning("rate limit hit for %s", key)
            raise TooManyLoginAttemptsError

    def record(self, key: str) -> None:
        self._prune(key).append(time.monotonic())

    def reset(self, key: str) -> None:
        self._events.pop(key, None)

    def _prune(self, key: str) -> deque[float]:
        events = self._events[key]
        cutoff = time.monotonic() - self.window_seconds
        while events and events[0] < cutoff:
            events.popleft()
        return events


class LoginRateLimiter(SlidingWindowRateLimiter):
    """Counts failed login attempts, keyed by client ip + username."""


class RegisterRateLimiter(SlidingWindowRateLimiter):
    """Counts sign-up attempts, keyed by client ip."""

    def __init__(self, max_events: int = 10, window_seconds: int = 60 * 60):
        super().__init__(max_events, window_seconds)
