"""SubIssueRemovedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class SubIssueRemovedEvent(Event):
    """Event representing a sub-issue being removed from an issue."""

    child_issue_number: Optional[int] = None
    child_issue_title: Optional[str] = None
    child_issue_url: Optional[str] = None
    child_repository_name: Optional[str] = None
    child_repository_owner: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "SubIssueRemovedEvent":
        """Create a SubIssueRemovedEvent instance from API response data."""
        event = super().from_response(data)

        child_issue_number = None
        child_issue_title = None
        child_issue_url = None
        child_repository_name = None
        child_repository_owner = None

        if data.get("subIssue") and data["subIssue"].get("__typename") == "Issue":
            child_issue = data["subIssue"]
            child_issue_number = child_issue.get("number")
            child_issue_title = child_issue.get("title")
            child_issue_url = child_issue.get("url")

            if child_issue.get("repository"):
                child_repository_name = child_issue["repository"].get("name")
                if child_issue["repository"].get("owner"):
                    child_repository_owner = child_issue["repository"]["owner"].get(
                        "login"
                    )

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            child_issue_number=child_issue_number,
            child_issue_title=child_issue_title,
            child_issue_url=child_issue_url,
            child_repository_name=child_repository_name,
            child_repository_owner=child_repository_owner,
        )
