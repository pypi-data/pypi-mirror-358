"""AddedToProjectEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class AddedToProjectEvent(Event):
    """Event representing an issue being added to a project."""

    project_name: str = ""
    project_url: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "AddedToProjectEvent":
        """Create an AddedToProjectEvent instance from API response data."""
        event = super().from_response(data)

        project_name = ""
        project_url = None
        if data.get("project") and data["project"] is not None:
            project_url = data["project"].get("url")
            project_name = data["project"].get("name", "")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            project_name=project_name,
            project_url=project_url,
        )
