"""TransferredEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class TransferredEvent(Event):
    """Event representing an issue being transferred to another repository."""

    from_repository_name: Optional[str] = None
    from_repository_owner: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "TransferredEvent":
        """Create a TransferredEvent instance from API response data."""
        event = super().from_response(data)

        from_repository_name = None
        from_repository_owner = None

        if data.get("fromRepository"):
            from_repository_name = data["fromRepository"].get("name")
            if data["fromRepository"].get("owner"):
                from_repository_owner = data["fromRepository"]["owner"].get("login")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            from_repository_name=from_repository_name,
            from_repository_owner=from_repository_owner,
        )
