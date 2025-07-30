"""PinnedEvent model class."""

from typing import Dict, Any
from dataclasses import dataclass
from .event import Event


@dataclass
class PinnedEvent(Event):
    """Event representing an issue being pinned."""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "PinnedEvent":
        """Create a PinnedEvent instance from API response data."""
        event = super().from_response(data)

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
        )
