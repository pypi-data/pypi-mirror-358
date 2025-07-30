"""UnassignedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class UnassignedEvent(Event):
    """Event representing a user being unassigned from an issue."""

    assignee_login: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "UnassignedEvent":
        """Create an UnassignedEvent instance from API response data."""
        event = super().from_response(data)

        assignee_login = None
        if data.get("assignee") and data["assignee"] is not None:
            assignee_login = data["assignee"].get("login")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            assignee_login=assignee_login,
        )
