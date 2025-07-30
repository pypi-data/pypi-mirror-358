"""Base Event model class for timeline events."""

from typing import Dict, Any, Optional, Type
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """Base class for all timeline events."""

    id: str
    created_at: datetime
    actor_login: Optional[str] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "Event":
        """Create an Event instance from API response data.

        Args:
            data (Dict[str, Any]): Raw event data from API response

        Returns:
            Event: New Event instance
        """
        actor_login = None
        if data.get("actor") and data["actor"] is not None:
            actor_login = data["actor"].get("login")

        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00")),
            actor_login=actor_login,
        )

    @staticmethod
    def create_from_response(data: Dict[str, Any]) -> Optional["Event"]:
        """Factory method to create the appropriate event type from response data.

        Args:
            data (Dict[str, Any]): Raw event data from API response

        Returns:
            Optional[Event]: Event instance of the appropriate subclass, or None if type not supported
        """
        from . import (
            AddedToProjectEvent,
            AssignedEvent,
            ClosedEvent,
            CommentDeletedEvent,
            CrossReferencedEvent,
            DemilestonedEvent,
            IssueCommentEvent,
            IssueTypeAddedEvent,
            IssueTypeChangedEvent,
            IssueTypeRemovedEvent,
            LabeledEvent,
            LockedEvent,
            MarkedAsDuplicateEvent,
            MentionedEvent,
            MergedEvent,
            MilestonedEvent,
            MovedColumnsInProjectEvent,
            ParentIssueAddedEvent,
            ParentIssueRemovedEvent,
            PinnedEvent,
            ReferencedEvent,
            RenamedTitleEvent,
            ReopenedEvent,
            SubIssueAddedEvent,
            SubIssueRemovedEvent,
            SubscribedEvent,
            TransferredEvent,
            UnassignedEvent,
            UnlabeledEvent,
            UnsubscribedEvent,
        )

        event_type = data.get("__typename")
        event_classes = {
            "AddedToProjectEvent": AddedToProjectEvent,
            "AssignedEvent": AssignedEvent,
            "ClosedEvent": ClosedEvent,
            "CommentDeletedEvent": CommentDeletedEvent,
            "CrossReferencedEvent": CrossReferencedEvent,
            "DemilestonedEvent": DemilestonedEvent,
            "IssueComment": IssueCommentEvent,
            "IssueTypeAddedEvent": IssueTypeAddedEvent,
            "IssueTypeChangedEvent": IssueTypeChangedEvent,
            "IssueTypeRemovedEvent": IssueTypeRemovedEvent,
            "LabeledEvent": LabeledEvent,
            "LockedEvent": LockedEvent,
            "MarkedAsDuplicateEvent": MarkedAsDuplicateEvent,
            "MentionedEvent": MentionedEvent,
            "MergedEvent": MergedEvent,
            "MilestonedEvent": MilestonedEvent,
            "MovedColumnsInProjectEvent": MovedColumnsInProjectEvent,
            "ParentIssueAddedEvent": ParentIssueAddedEvent,
            "ParentIssueRemovedEvent": ParentIssueRemovedEvent,
            "PinnedEvent": PinnedEvent,
            "ReferencedEvent": ReferencedEvent,
            "RenamedTitleEvent": RenamedTitleEvent,
            "ReopenedEvent": ReopenedEvent,
            "SubIssueAddedEvent": SubIssueAddedEvent,
            "SubIssueRemovedEvent": SubIssueRemovedEvent,
            "SubscribedEvent": SubscribedEvent,
            "TransferredEvent": TransferredEvent,
            "UnassignedEvent": UnassignedEvent,
            "UnlabeledEvent": UnlabeledEvent,
            "UnsubscribedEvent": UnsubscribedEvent,
        }

        if event_type in event_classes:
            return event_classes[event_type].from_response(data)
        return None
