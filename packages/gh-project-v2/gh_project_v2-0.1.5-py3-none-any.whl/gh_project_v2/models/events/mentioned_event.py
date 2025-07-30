"""MentionedEvent model class."""

from typing import Dict, Any
from dataclasses import dataclass
from .event import Event


@dataclass
class MentionedEvent(Event):
    """Event representing a user being mentioned in an issue."""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "MentionedEvent":
        """Create a MentionedEvent instance from API response data."""
        event = super().from_response(data)

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
        )
