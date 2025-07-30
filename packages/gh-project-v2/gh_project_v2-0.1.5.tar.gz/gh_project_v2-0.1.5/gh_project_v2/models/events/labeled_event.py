"""LabeledEvent model class."""

from typing import Dict, Any
from dataclasses import dataclass
from .event import Event


@dataclass
class LabeledEvent(Event):
    """Event representing a label being added to an issue."""

    label_name: str = ""
    label_color: str = ""

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "LabeledEvent":
        """Create a LabeledEvent instance from API response data."""
        event = super().from_response(data)

        label = data.get("label", {})

        return cls(
            id=event.id,
            created_at=event.created_at,
            actor_login=event.actor_login,
            label_name=label.get("name", ""),
            label_color=label.get("color", ""),
        )
