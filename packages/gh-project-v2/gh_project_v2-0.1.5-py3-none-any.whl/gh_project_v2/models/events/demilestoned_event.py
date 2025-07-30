"""DemilestonedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class DemilestonedEvent(Event):
    """Event representing an issue being removed from a milestone."""

    milestone_title: Optional[str] = None
    subject_number: Optional[int] = None
    subject_title: Optional[str] = None
    subject_url: Optional[str] = None
    subject_repository_name: Optional[str] = None
    subject_repository_owner: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "DemilestonedEvent":
        """Create a DemilestonedEvent instance from API response data."""
        event = super().from_response(data)

        milestone_title = data.get("milestoneTitle")
        subject_number = None
        subject_title = None
        subject_url = None
        subject_repository_name = None
        subject_repository_owner = None

        if data.get("subject") and data["subject"] is not None:
            subject = data["subject"]
            subject_number = subject.get("number")
            subject_title = subject.get("title")
            subject_url = subject.get("url")

            if subject.get("repository"):
                subject_repository_name = subject["repository"].get("name")
                if subject["repository"].get("owner"):
                    subject_repository_owner = subject["repository"]["owner"].get(
                        "login"
                    )

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            milestone_title=milestone_title,
            subject_number=subject_number,
            subject_title=subject_title,
            subject_url=subject_url,
            subject_repository_name=subject_repository_name,
            subject_repository_owner=subject_repository_owner,
        )
