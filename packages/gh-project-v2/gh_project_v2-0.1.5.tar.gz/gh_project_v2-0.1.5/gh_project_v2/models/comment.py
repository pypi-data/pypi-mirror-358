"""Issue Comment model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..client import GraphQLClient
from ..queries import load_query


@dataclass
class Comment:
    """Represents a comment on a GitHub issue."""

    id: str
    body: str
    author_login: str
    url: str
    created_at: datetime
    updated_at: datetime
    client: Optional[GraphQLClient] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any], client: Optional[GraphQLClient] = None) -> "Comment":
        """Create a Comment instance from API response data.

        Args:
            data (Dict[str, Any]): Raw comment data from API response
            client (Optional[GraphQLClient]): GraphQL client for API calls

        Returns:
            Comment: New Comment instance
        """
        return cls(
            id=data["id"],
            body=data["body"],
            author_login=data["author"]["login"],
            url=data["url"],
            created_at=datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00")),
            client=client,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        id: str
    ) -> "Comment":
        """Get a comment's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            id (str): Comment node ID
            
        Returns:
            Comment: Self with populated properties
            
        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_comment")
        variables = {
            "id": id
        }
        
        response = client.execute(query, variables)
        
        # Use from_response to create a comment instance with all properties
        comment = Comment.from_response(response["node"], client)
        
        # Update this instance's attributes with the fetched data
        self.id = comment.id
        self.body = comment.body
        self.author_login = comment.author_login
        self.url = comment.url
        self.created_at = comment.created_at
        self.updated_at = comment.updated_at
        self.client = client
        
        return self
