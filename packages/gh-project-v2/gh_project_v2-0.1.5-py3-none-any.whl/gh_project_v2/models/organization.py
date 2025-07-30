"""Organization model class for GitHub API responses."""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any

from ..client import GraphQLClient
from ..queries import load_query
from .repository import Repository
from .user import User


@dataclass
class Organization:
    """Represents a GitHub organization."""

    id: str
    login: str
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    client: Optional[GraphQLClient] = None

    @classmethod
    def from_response(cls, response: dict, client: Optional[GraphQLClient] = None) -> "Organization":
        """Create Organization instance from GraphQL response.

        Args:
            response (dict): GraphQL response data containing organization info
            client (Optional[GraphQLClient]): GraphQL client for API calls

        Returns:
            Organization: New Organization instance
        """
        # For node query the data is in ["node"], for direct query in ["organization"]
        if "node" in response:
            org_data = response["node"]
        else:
            org_data = response.get("organization", {})
            
        return cls(
            id=org_data["id"],
            login=org_data["login"],
            name=org_data.get("name"),
            description=org_data.get("description"),
            url=org_data.get("url"),
            location=org_data.get("location"),
            website_url=org_data.get("websiteUrl"),
            client=client,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        id: Optional[str] = None,
        name: Optional[str] = None
    ) -> "Organization":
        """Get an organization's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            id (Optional[str]): Organization ID (for lookup by ID)
            name (Optional[str]): Organization name/login (for lookup by name)
            
        Returns:
            Organization: Self with populated properties
            
        Raises:
            ValueError: If neither id nor name is provided
            GraphQLError: On GraphQL operation failures
        """
        if not id and not name:
            raise ValueError("Either id or name must be provided")
            
        if id:
            query = load_query("get_organization_by_id")
            variables = {"id": id}
        else:
            query = load_query("get_organization")
            variables = {"login": name}
        
        response = client.execute(query, variables)
        
        # Use from_response to create an organization instance with all properties
        org = Organization.from_response(response, client)
        
        # Update this instance's attributes with the fetched data
        self.id = org.id
        self.login = org.login
        self.name = org.name
        self.description = org.description
        self.url = org.url
        self.location = org.location
        self.website_url = org.website_url
        self.client = client
        
        return self
        
    def get_repos(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get repositories belonging to this organization.
        
        Args:
            first (int, optional): Number of repositories to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of Repository objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set or login is not set
            GraphQLError: On GraphQL operation failures
        """
        if not self.client:
            raise ValueError("Client must be set to fetch repositories")
        
        if not self.login:
            raise ValueError("Organization login must be set to fetch repositories")
            
        query = load_query("get_organization_repos")
        variables = {
            "login": self.login,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        repos_data = response["organization"]["repositories"]
        
        # Convert each node to a Repository object
        repos_data["nodes"] = [
            Repository.from_response({"repository": repo}, self.client) for repo in repos_data["nodes"]
        ]
        
        return repos_data
        
    def get_users(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get users (members) belonging to this organization.
        
        Args:
            first (int, optional): Number of users to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of User objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set or login is not set
            GraphQLError: On GraphQL operation failures
        """
        if not self.client:
            raise ValueError("Client must be set to fetch users")
        
        if not self.login:
            raise ValueError("Organization login must be set to fetch users")
            
        query = load_query("get_organization_users")
        variables = {
            "login": self.login,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        users_data = response["organization"]["membersWithRole"]
        
        # Convert each node to a User object
        users_data["nodes"] = [
            User.from_response({"user": user}, self.client) for user in users_data["nodes"]
        ]
        
        return users_data
