"""User model class."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..client import GraphQLClient
from ..queries import load_query


@dataclass
class User:
    """Represents a GitHub User with basic profile information."""

    id: str
    login: str
    name: Optional[str]
    email: Optional[str]
    bio: Optional[str]
    company: Optional[str]
    location: Optional[str]
    website_url: Optional[str]
    url: str
    avatar_url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    client: Optional[GraphQLClient] = None

    def __post_init__(self):
        """Initialize default values for datetime fields."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    @classmethod
    def from_response(cls, data: Dict[str, Any], client: Optional[GraphQLClient] = None) -> "User":
        """Create a User instance from API response data.

        Args:
            data (Dict[str, Any]): Raw user data from API response
            client (Optional[GraphQLClient]): GraphQL client for API calls

        Returns:
            User: New User instance
        """
        # Handle responses from node query or direct user query
        if "node" in data:
            user_data = data["node"]
        else:
            # For responses that have user data nested under 'user' key
            user_data = data.get("user", data)

        return cls(
            id=user_data["id"],
            login=user_data["login"],
            name=user_data.get("name"),
            email=user_data.get("email"),
            bio=user_data.get("bio"),
            company=user_data.get("company"),
            location=user_data.get("location"),
            website_url=user_data.get("websiteUrl"),
            url=user_data["url"],
            avatar_url=user_data["avatarUrl"],
            created_at=datetime.fromisoformat(
                user_data["createdAt"].replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                user_data["updatedAt"].replace("Z", "+00:00")
            ),
            client=client,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        id: Optional[str] = None,
        username: Optional[str] = None
    ) -> "User":
        """Get a user's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            id (Optional[str]): User ID (for lookup by ID)
            username (Optional[str]): Username (for lookup by username)
            
        Returns:
            User: Self with populated properties
            
        Raises:
            ValueError: If neither id nor username is provided
            GraphQLError: On GraphQL operation failures
        """
        if not id and not username:
            raise ValueError("Either id or username must be provided")
            
        if id:
            query = load_query("get_user_by_id")
            variables = {"id": id}
        else:
            query = load_query("get_user")
            variables = {"login": username}
        
        response = client.execute(query, variables)
        
        # Use from_response to create a user instance with all properties
        user = User.from_response(response, client)
        
        # Update this instance's attributes with the fetched data
        self.id = user.id
        self.login = user.login
        self.name = user.name
        self.email = user.email
        self.bio = user.bio
        self.company = user.company
        self.location = user.location
        self.website_url = user.website_url
        self.url = user.url
        self.avatar_url = user.avatar_url
        self.created_at = user.created_at
        self.updated_at = user.updated_at
        self.client = client
        
        return self
        
    def get_followers(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get followers of this user.
        
        Args:
            first (int, optional): Number of followers to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of User objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set
            GraphQLError: On GraphQL operation failures
        """
        if not self.client:
            raise ValueError("Client must be set to fetch followers")
            
        query = load_query("get_user_followers")
        variables = {
            "login": self.login,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        followers_data = response["user"]["followers"]
        
        # Convert each node to a User object
        followers_data["nodes"] = [
            User.from_response({"user": follower}, self.client) 
            for follower in followers_data["nodes"]
        ]
        
        return followers_data
        
    def get_following(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get users followed by this user.
        
        Args:
            first (int, optional): Number of following users to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of User objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set
            GraphQLError: On GraphQL operation failures
        """
        if not self.client:
            raise ValueError("Client must be set to fetch following users")
            
        query = load_query("get_user_following")
        variables = {
            "login": self.login,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        following_data = response["user"]["following"]
        
        # Convert each node to a User object
        following_data["nodes"] = [
            User.from_response({"user": following}, self.client) 
            for following in following_data["nodes"]
        ]
        
        return following_data
        
    def get_issues(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get issues assigned to this user.
        
        Args:
            first (int, optional): Number of issues to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of Issue objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set
            GraphQLError: On GraphQL operation failures
        """
        from .issue import Issue
        
        if not self.client:
            raise ValueError("Client must be set to fetch user issues")
            
        query = load_query("get_user_issues")
        variables = {
            "login": self.login,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        issues_data = response["user"]["issues"]
        
        # Convert each node to an Issue object
        issues_data["nodes"] = [
            Issue(
                id=issue_data["id"],
                number=issue_data["number"],
                title=issue_data["title"],
                url=issue_data["url"],
                state=issue_data["state"],
                created_at=datetime.fromisoformat(issue_data["createdAt"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(issue_data["updatedAt"].replace("Z", "+00:00")),
                author_login=issue_data["author"]["login"],
                body=issue_data.get("body"),
                field_values=[],
                client=self.client,
                owner=issue_data["repository"]["owner"]["login"],
                repo=issue_data["repository"]["name"]
            )
            for issue_data in issues_data["nodes"]
        ]
        
        return issues_data
