"""Base utilities for profiling code."""

from time import perf_counter


class WallClock:
    """
    Context manager to measure wall time.

    Just for convenience. Though it violates some flake8 rules (WPS441).
    And maybe it is also an overkill. But let it be here.
    """

    def __init__(self) -> None:
        self._start: float = 0
        self._end: float = 0
        self._wall_time: float = -1

    def __enter__(self):
        self._start = perf_counter()
        return self

    def __exit__(self, *_):
        self._end = perf_counter()
        self._wall_time = self._end - self._start

    def wall_time(self) -> float:
        """Return the wall time in seconds."""
        if self._wall_time < 0:
            raise ValueError(
                "Timer is not exited yet.\n"
                "Call `wall_time` outside of the context manager."
            )
        return self._wall_time
