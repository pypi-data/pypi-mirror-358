"""CrossReferencedEvent model class."""

from typing import Dict, Any
from dataclasses import dataclass
from .event import Event


@dataclass
class CrossReferencedEvent(Event):
    """Event representing an issue being cross-referenced."""

    source_repository_name: str = ""
    source_repository_owner: str = ""
    source_issue_number: int = 0
    source_issue_title: str = ""
    source_url: str = ""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "CrossReferencedEvent":
        """Create a CrossReferencedEvent instance from API response data."""
        event = super().from_response(data)

        source = data.get("source", {})
        repo = {}
        owner = ""
        if "repository" in source:
            repo = source["repository"] or {}
            if "owner" in repo:
                owner = repo.get("owner", {}).get("login", "")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            source_repository_name=repo.get("name", ""),
            source_repository_owner=owner,
            source_issue_number=source.get("number", 0),
            source_issue_title=source.get("title", ""),
            source_url=source.get("url", ""),
        )
