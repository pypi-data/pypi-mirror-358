"""CommentDeletedEvent model class."""

from typing import Dict, Any
from dataclasses import dataclass
from .event import Event


@dataclass
class CommentDeletedEvent(Event):
    """Event representing a comment being deleted."""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "CommentDeletedEvent":
        """Create a CommentDeletedEvent instance from API response data."""
        event = super().from_response(data)

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
        )
