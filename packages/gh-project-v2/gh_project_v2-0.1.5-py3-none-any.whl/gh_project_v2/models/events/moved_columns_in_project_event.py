"""MovedColumnsInProjectEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class MovedColumnsInProjectEvent(Event):
    """Event representing an issue being moved between columns in a project."""

    project_name: str = ""
    project_url: Optional[str] = None
    previous_column_name: Optional[str] = None
    current_column_name: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "MovedColumnsInProjectEvent":
        """Create a MovedColumnsInProjectEvent instance from API response data."""
        event = super().from_response(data)

        project_name = ""
        project_url = None
        previous_column_name = None
        current_column_name = None

        if data.get("project") and data["project"] is not None:
            project_url = data["project"].get("url")
            project_name = data["project"].get("name", "")

        if data.get("previousProjectColumnName"):
            previous_column_name = data["previousProjectColumnName"]

        if data.get("projectColumnName"):
            current_column_name = data["projectColumnName"]

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            project_name=project_name,
            project_url=project_url,
            previous_column_name=previous_column_name,
            current_column_name=current_column_name,
        )
