"""RenamedTitleEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class RenamedTitleEvent(Event):
    """Event representing an issue's title being renamed."""

    previous_title: Optional[str] = None
    current_title: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "RenamedTitleEvent":
        """Create a RenamedTitleEvent instance from API response data."""
        event = super().from_response(data)

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            previous_title=data.get("previousTitle"),
            current_title=data.get("currentTitle"),
        )
