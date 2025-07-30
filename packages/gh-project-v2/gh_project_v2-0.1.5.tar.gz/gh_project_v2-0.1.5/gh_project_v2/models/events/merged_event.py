"""MergedEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class MergedEvent(Event):
    """Event representing a pull request being merged."""

    merge_commit_sha: Optional[str] = None
    merge_ref_name: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "MergedEvent":
        """Create a MergedEvent instance from API response data."""
        event = super().from_response(data)

        merge_commit_sha = (
            data.get("commit", {}).get("oid") if data.get("commit") else None
        )
        merge_ref_name = data.get("mergeRefName")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            merge_commit_sha=merge_commit_sha,
            merge_ref_name=merge_ref_name,
        )
