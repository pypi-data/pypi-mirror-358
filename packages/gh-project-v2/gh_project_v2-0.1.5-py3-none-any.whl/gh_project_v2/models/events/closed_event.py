"""ClosedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class ClosedEvent(Event):
    """Event representing an issue being closed."""

    state_reason: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "ClosedEvent":
        """Create a ClosedEvent instance from API response data."""
        event = super().from_response(data)

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            state_reason=data.get("stateReason"),
        )
