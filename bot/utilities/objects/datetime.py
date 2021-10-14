# Future
from __future__ import annotations

# Standard Library
import datetime as dt

# Packages
import pendulum


class PastPhrasedDatetimeSearch:

    def __init__(
        self,
        phrase: str,
        *,
        datetimes: list[tuple[str, dt.datetime]]
    ) -> None:

        self._phrase: str = phrase
        self._datetimes: dict[str, pendulum.DateTime] = {phrase: pendulum.instance(datetime, tz="UTC") for phrase, datetime in datetimes}

    @property
    def phrase(self) -> str:
        return self._phrase

    @property
    def datetimes(self) -> dict[str, pendulum.DateTime]:
        return self._datetimes


class FuturePhrasedDatetimeSearch(PastPhrasedDatetimeSearch):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
