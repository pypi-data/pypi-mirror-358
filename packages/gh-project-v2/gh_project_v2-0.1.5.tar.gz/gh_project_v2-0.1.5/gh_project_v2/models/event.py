"""Issue Timeline Event model classes - compatibility import."""

# Import all event classes from the new location for backward compatibility
from .events import (
    Event, AddedToProjectEvent, AssignedEvent, ClosedEvent, CommentDeletedEvent,
    CrossReferencedEvent, IssueCommentEvent, IssueTypeAddedEvent, IssueTypeChangedEvent,
    LabeledEvent, MentionedEvent, RenamedTitleEvent, SubIssueAddedEvent, 
    SubIssueRemovedEvent, TransferredEvent
)

__all__ = [
    "Event", "AddedToProjectEvent", "AssignedEvent", "ClosedEvent", "CommentDeletedEvent",
    "CrossReferencedEvent", "IssueCommentEvent", "IssueTypeAddedEvent", "IssueTypeChangedEvent",
    "LabeledEvent", "MentionedEvent", "RenamedTitleEvent", "SubIssueAddedEvent", 
    "SubIssueRemovedEvent", "TransferredEvent"
]