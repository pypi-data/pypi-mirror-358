"""AssignedEvent model class."""

from typing import Dict, Any
from dataclasses import dataclass
from .event import Event


@dataclass
class AssignedEvent(Event):
    """Event representing an issue being assigned to a user."""

    assignee_login: str = ""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "AssignedEvent":
        """Create an AssignedEvent instance from API response data."""
        event = super().from_response(data)

        assignee_login = ""
        if data.get("assignee") and data["assignee"] is not None:
            assignee_login = data["assignee"].get("login", "")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            assignee_login=assignee_login,
        )
