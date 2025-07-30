"""LockedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class LockedEvent(Event):
    """Event representing an issue being locked."""

    lock_reason: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "LockedEvent":
        """Create a LockedEvent instance from API response data."""
        event = super().from_response(data)

        lock_reason = data.get("lockReason")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            lock_reason=lock_reason,
        )
