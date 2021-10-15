# Future
from __future__ import annotations


class Time:

    def __init__(self, *, seconds: int) -> None:
        self._seconds = seconds

    @property
    def seconds(self) -> int:
        return self._seconds
