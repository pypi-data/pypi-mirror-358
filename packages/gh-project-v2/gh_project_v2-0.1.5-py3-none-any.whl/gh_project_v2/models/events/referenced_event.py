"""ReferencedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class ReferencedEvent(Event):
    """Event representing an issue being referenced by another issue or pull request."""

    source_issue_number: Optional[int] = None
    source_issue_title: str = ""
    source_issue_url: Optional[str] = None
    source_repository_name: str = ""
    source_repository_owner: str = ""
    reference_type: str = ""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "ReferencedEvent":
        """Create a ReferencedEvent instance from API response data."""
        event = super().from_response(data)

        source_issue_number = None
        source_issue_title = ""
        source_issue_url = None
        source_repository_name = ""
        source_repository_owner = ""
        reference_type = ""

        if data.get("subject") and data["subject"] is not None:
            source = data["subject"]
            reference_type = source.get("__typename", "")
            source_issue_number = source.get("number")
            source_issue_title = source.get("title", "")
            source_issue_url = source.get("url")

            if source.get("repository") and source["repository"] is not None:
                repository = source["repository"]
                source_repository_name = repository.get("name", "")

                if repository.get("owner") and repository["owner"] is not None:
                    source_repository_owner = repository["owner"].get("login", "")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            source_issue_number=source_issue_number,
            source_issue_title=source_issue_title,
            source_issue_url=source_issue_url,
            source_repository_name=source_repository_name,
            source_repository_owner=source_repository_owner,
            reference_type=reference_type,
        )
