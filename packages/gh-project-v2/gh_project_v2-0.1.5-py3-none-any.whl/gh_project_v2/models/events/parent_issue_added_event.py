"""ParentIssueAddedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class ParentIssueAddedEvent(Event):
    """Event representing a parent issue being added to an issue."""

    parent_issue_number: Optional[int] = None
    parent_issue_title: str = ""
    parent_issue_url: Optional[str] = None
    parent_repository_name: str = ""
    parent_repository_owner: str = ""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "ParentIssueAddedEvent":
        """Create a ParentIssueAddedEvent instance from API response data."""
        event = super().from_response(data)

        parent_issue_number = None
        parent_issue_title = ""
        parent_issue_url = None
        parent_repository_name = ""
        parent_repository_owner = ""

        if data.get("parent") and data["parent"] is not None:
            parent_issue = data["parent"]
            parent_issue_number = parent_issue.get("number")
            parent_issue_title = parent_issue.get("title", "")
            parent_issue_url = parent_issue.get("url")

            if (
                parent_issue.get("repository")
                and parent_issue["repository"] is not None
            ):
                repository = parent_issue["repository"]
                parent_repository_name = repository.get("name", "")

                if repository.get("owner") and repository["owner"] is not None:
                    parent_repository_owner = repository["owner"].get("login", "")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            parent_issue_number=parent_issue_number,
            parent_issue_title=parent_issue_title,
            parent_issue_url=parent_issue_url,
            parent_repository_name=parent_repository_name,
            parent_repository_owner=parent_repository_owner,
        )
