"""Project Draft Issue model class."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from ..client import GraphQLClient
from ..queries import load_query
from .field import Field
from .issue import Issue


@dataclass
class DraftIssue(Issue):
    """Represents a draft issue in a GitHub Project (V2)."""

    @classmethod
    def from_response(
        cls,
        data: Dict[str, Any],
        client: Optional[GraphQLClient] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> "DraftIssue":
        """Create a DraftIssue instance from API response data.

        Args:
            data (Dict[str, Any]): Raw draft issue data from API response
            client (Optional[GraphQLClient]): GraphQL client for API calls
            owner (Optional[str]): Owner of the repository
            repo (Optional[str]): Repository name

        Returns:
            DraftIssue: New DraftIssue instance
        """
        # Handle DraftIssue which has different fields than regular Issues
        if "content" in data:  # Project item response
            content = data["content"]
            return cls(
                id=content["id"],
                number=0,  # DraftIssue doesn't have a number
                title=content["title"],
                url="",  # DraftIssue doesn't have a URL
                state="",  # DraftIssue doesn't have a state
                created_at=datetime.fromisoformat(
                    content["createdAt"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    content["updatedAt"].replace("Z", "+00:00")
                ),
                author_login=content.get("creator", {}).get("login", ""),
                body=content.get("body"),
                field_values=data.get("fieldValues", {"nodes": []})["nodes"],
                client=client,
                owner=owner,
                repo=repo,
            )
        else:  # Draft issue-specific response
            # For search results the data is in ["node"], directly in data
            if "node" in data:
                issue_data = data["node"]
            else:
                issue_data = data

            return cls(
                id=issue_data["id"],
                number=0,  # DraftIssue doesn't have a number
                title=issue_data["title"],
                url="",  # DraftIssue doesn't have a URL
                state="",  # DraftIssue doesn't have a state
                created_at=datetime.fromisoformat(
                    issue_data["createdAt"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    issue_data["updatedAt"].replace("Z", "+00:00")
                ),
                author_login=issue_data.get("creator", {}).get("login", ""),
                body=issue_data.get("body"),
                field_values=[],  # Not included in issue responses
                client=client,
                owner=owner,
                repo=repo,
            )