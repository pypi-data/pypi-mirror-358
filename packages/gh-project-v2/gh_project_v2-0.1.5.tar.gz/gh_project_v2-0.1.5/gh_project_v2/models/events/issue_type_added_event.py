"""IssueTypeAddedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class IssueTypeAddedEvent(Event):
    """Event representing an issue type being added."""

    issue_type_id: Optional[str] = None
    issue_type_name: Optional[str] = None
    issue_type_description: Optional[str] = None
    issue_type_color: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "IssueTypeAddedEvent":
        """Create an IssueTypeAddedEvent instance from API response data."""
        event = super().from_response(data)

        issue_type_id = None
        issue_type_name = None
        issue_type_description = None
        issue_type_color = None

        if data.get("issueType") and data["issueType"] is not None:
            issue_type = data["issueType"]
            issue_type_id = issue_type.get("id")
            issue_type_name = issue_type.get("name")
            issue_type_description = issue_type.get("description")
            issue_type_color = issue_type.get("color")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            issue_type_id=issue_type_id,
            issue_type_name=issue_type_name,
            issue_type_description=issue_type_description,
            issue_type_color=issue_type_color,
        )
