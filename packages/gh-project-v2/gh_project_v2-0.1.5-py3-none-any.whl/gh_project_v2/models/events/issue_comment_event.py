"""IssueCommentEvent model class."""

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from .event import Event


@dataclass
class IssueCommentEvent(Event):
    """Represents a comment on a GitHub issue."""

    body: str = ""
    url: str = ""
    updated_at: datetime = field(default_factory=lambda: datetime.now())

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "IssueCommentEvent":
        """Create an IssueCommentEvent instance from API response data."""
        event = super().from_response(data)

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            body=data.get("body", ""),
            url=data.get("url", ""),
            updated_at=datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00")),
        )
