"""ReopenedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class ReopenedEvent(Event):
    """Event representing an issue being reopened."""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "ReopenedEvent":
        """Create a ReopenedEvent instance from API response data."""
        event = super().from_response(data)

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
        )
