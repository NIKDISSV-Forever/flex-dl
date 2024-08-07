from __future__ import annotations


class MapKeyError(KeyError):
    __slots__ = ('key', 'at', 'format_map',)

    def __init__(self, key: str, at: str, format_map: dict):
        self.format_map = format_map
        self.at = at
        self.key = key

    def __str__(self):
        return f"Unknown keys {', '.join(map(repr, self.args))} at {self.at!r}"
