"""UnlabeledEvent model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .event import Event


@dataclass
class UnlabeledEvent(Event):
    """Event representing a label being removed from an issue."""

    label_name: str = ""
    label_color: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "UnlabeledEvent":
        """Create an UnlabeledEvent instance from API response data."""
        event = super().from_response(data)

        label_name = ""
        label_color = None
        if data.get("label") and data["label"] is not None:
            label_name = data["label"].get("name", "")
            label_color = data["label"].get("color")

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            label_name=label_name,
            label_color=label_color,
        )
