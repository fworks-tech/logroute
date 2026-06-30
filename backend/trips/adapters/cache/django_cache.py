from typing import Any

from django.core.cache import cache


class DjangoCache:
    def get(self, key: str) -> Any | None:
        return cache.get(key)

    def set(self, key: str, value: Any, timeout: int) -> None:
        cache.set(key, value, timeout)

    def delete(self, key: str) -> None:
        cache.delete(key)

    def clear(self) -> None:
        try:
            cache.clear()
        except ConnectionError:
            pass
