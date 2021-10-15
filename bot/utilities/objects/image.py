# Future
from __future__ import annotations


class Image:

    def __init__(self, url: str) -> None:
        self._url = url

    @property
    def url(self) -> str:
        return self._url
