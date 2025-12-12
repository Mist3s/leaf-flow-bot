from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReplyTarget:
    user_telegram_id: int
    order_id: Optional[str] = None


class MappingStore:
    """In-memory mapping between admin prompt messages and targets."""

    def __init__(self) -> None:
        self._storage: dict[int, ReplyTarget] = {}

    def set_mapping(self, admin_message_id: int, target: ReplyTarget) -> None:
        self._storage[admin_message_id] = target

    def get_target(self, admin_message_id: int) -> ReplyTarget | None:
        return self._storage.get(admin_message_id)

    def clear(self) -> None:
        self._storage.clear()
