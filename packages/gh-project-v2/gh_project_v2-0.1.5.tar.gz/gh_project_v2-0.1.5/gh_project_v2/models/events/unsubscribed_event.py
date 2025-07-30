"""UnsubscribedEvent model class."""

from typing import Dict, Any
from dataclasses import dataclass
from .event import Event


@dataclass
class UnsubscribedEvent(Event):
    """Event representing a user unsubscribing from an issue."""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "UnsubscribedEvent":
        """Create an UnsubscribedEvent instance from API response data."""
        event = super().from_response(data)

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
        )
