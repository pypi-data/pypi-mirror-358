"""MarkedAsDuplicateEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class MarkedAsDuplicateEvent(Event):
    """Event representing an issue being marked as a duplicate of another issue."""

    canonical_number: Optional[int] = None
    canonical_title: Optional[str] = None
    canonical_url: Optional[str] = None
    canonical_repository_name: Optional[str] = None
    canonical_repository_owner: Optional[str] = None

    duplicate_number: Optional[int] = None
    duplicate_title: Optional[str] = None
    duplicate_url: Optional[str] = None
    duplicate_repository_name: Optional[str] = None
    duplicate_repository_owner: Optional[str] = None
    
    # Support for legacy format
    duplicate_id: Optional[str] = None
    duplicate_name: Optional[str] = None
    duplicate_description: Optional[str] = None
    duplicate_color: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "MarkedAsDuplicateEvent":
        """Create a MarkedAsDuplicateEvent instance from API response data."""
        event = super().from_response(data)

        canonical_number = None
        canonical_title = None
        canonical_url = None
        canonical_repository_name = None
        canonical_repository_owner = None

        duplicate_number = None
        duplicate_title = None
        duplicate_url = None
        duplicate_repository_name = None
        duplicate_repository_owner = None
        
        # Legacy format support
        duplicate_id = None
        duplicate_name = None
        duplicate_description = None
        duplicate_color = None

        if data.get("canonical") and data["canonical"] is not None:
            canonical = data["canonical"]
            canonical_number = canonical.get("number")
            canonical_title = canonical.get("title")
            canonical_url = canonical.get("url")

            if canonical.get("repository"):
                canonical_repository_name = canonical["repository"].get("name")
                if canonical["repository"].get("owner"):
                    canonical_repository_owner = canonical["repository"]["owner"].get(
                        "login"
                    )

        if data.get("duplicate") and data["duplicate"] is not None:
            duplicate = data["duplicate"]
            
            # Check if it's the new format (Issue or PullRequest)
            if "number" in duplicate:
                duplicate_number = duplicate.get("number")
                duplicate_title = duplicate.get("title")
                duplicate_url = duplicate.get("url")
                
                if duplicate.get("repository"):
                    duplicate_repository_name = duplicate["repository"].get("name")
                    if duplicate["repository"].get("owner"):
                        duplicate_repository_owner = duplicate["repository"]["owner"].get(
                            "login"
                        )
            # Legacy format support
            else:
                duplicate_id = duplicate.get("id")
                duplicate_name = duplicate.get("name")
                duplicate_description = duplicate.get("description")
                duplicate_color = duplicate.get("color")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            canonical_number=canonical_number,
            canonical_title=canonical_title,
            canonical_url=canonical_url,
            canonical_repository_name=canonical_repository_name,
            canonical_repository_owner=canonical_repository_owner,
            duplicate_number=duplicate_number,
            duplicate_title=duplicate_title,
            duplicate_url=duplicate_url,
            duplicate_repository_name=duplicate_repository_name,
            duplicate_repository_owner=duplicate_repository_owner,
            duplicate_id=duplicate_id,
            duplicate_name=duplicate_name,
            duplicate_description=duplicate_description,
            duplicate_color=duplicate_color,
        )
