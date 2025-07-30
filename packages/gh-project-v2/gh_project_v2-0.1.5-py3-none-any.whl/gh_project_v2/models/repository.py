"""Repository model class for GitHub API responses."""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any
import copy

from ..client import GraphQLClient
from ..queries import load_query
from .label import Label
from .pull_request import PullRequest


@dataclass(eq=True, frozen=True)
class Repository:
    """Represents a GitHub repository."""

    id: str = ""
    name: str = ""
    name_with_owner: str = ""
    url: str = ""
    owner_login: str = ""
    owner_url: str = ""
    description: Optional[str] = None
    is_private: bool = False
    homepage_url: Optional[str] = None
    client: Optional[GraphQLClient] = None

    def __hash__(self):
        """Make Repository hashable by its id."""
        return hash(self.id)

    @classmethod
    def from_response(cls, response: dict, client: Optional[GraphQLClient] = None) -> "Repository":
        """Create Repository instance from GraphQL response.

        Args:
            response (dict): GraphQL response data containing repository info
            client (Optional[GraphQLClient]): GraphQL client for API calls

        Returns:
            Repository: New Repository instance
        """
        repo_data = response.get("repository", {})
        owner = repo_data.get("owner", {})

        return cls(
            id=repo_data["id"],
            name=repo_data["name"],
            name_with_owner=repo_data["nameWithOwner"],
            url=repo_data["url"],
            owner_login=owner["login"],
            owner_url=owner["url"],
            description=repo_data.get("description"),
            is_private=repo_data.get("isPrivate", False),
            homepage_url=repo_data.get("homepageUrl"),
            client=client,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        name: str,
        org: Optional[str] = None,
        username: Optional[str] = None
    ) -> "Repository":
        """Get a repository's details.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            name (str): Repository name
            org (Optional[str]): Organization name (if repository belongs to an org)
            username (Optional[str]): Username (if repository belongs to a user)
            
        Returns:
            Repository: New Repository instance with populated properties
            
        Raises:
            ValueError: If neither org nor username is provided
            GraphQLError: On GraphQL operation failures
        """
        if not org and not username:
            raise ValueError("Either org or username must be provided")
            
        owner = org if org else username
        query = load_query("get_repository")
        variables = {
            "owner": owner,
            "name": name
        }
        
        response = client.execute(query, variables)
        
        # Use from_response to create a repository instance with all properties including client
        return Repository.from_response(response, client)
        
    def get_labels(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get labels for this repository.
        
        Args:
            first (int, optional): Number of labels to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of Label objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set or owner_login/name are not set
            GraphQLError: On GraphQL operation failures
        """
        if not self.client:
            raise ValueError("Client must be set to fetch labels")
        
        if not self.owner_login or not self.name:
            raise ValueError("Repository owner_login and name must be set to fetch labels")
            
        query = load_query("get_repository_labels")
        variables = {
            "owner": self.owner_login,
            "repo": self.name,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        labels_data = response["repository"]["labels"]
        
        # Convert each node to a Label object
        labels_data["nodes"] = [
            Label(
                id=label["id"],
                name=label["name"],
                color=label["color"],
                description=label.get("description"),
                url=label.get("url"),
                created_at=Label.from_response({"repository": {"label": label}}, self.client).created_at,
                updated_at=Label.from_response({"repository": {"label": label}}, self.client).updated_at,
                is_default=label.get("isDefault", False),
                client=self.client
            ) for label in labels_data["nodes"]
        ]
        
        return labels_data
        
    def get_pull_requests(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get pull requests for this repository.
        
        Args:
            first (int, optional): Number of pull requests to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of PullRequest objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set or owner_login/name are not set
            GraphQLError: On GraphQL operation failures
        """
        if not self.client:
            raise ValueError("Client must be set to fetch pull requests")
        
        if not self.owner_login or not self.name:
            raise ValueError("Repository owner_login and name must be set to fetch pull requests")
            
        query = load_query("get_repository_pull_requests")
        variables = {
            "owner": self.owner_login,
            "repo": self.name,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        prs_data = response["repository"]["pullRequests"]
        
        # Convert each node to a PullRequest object
        prs_data["nodes"] = [
            PullRequest.from_response(pr, self.client, self.owner_login, self.name) 
            for pr in prs_data["nodes"]
        ]
        
        return prs_data
    
    def get_issues(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get issues for this repository.
        
        Args:
            first (int, optional): Number of issues to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of Issue objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set or owner_login/name are not set
            GraphQLError: On GraphQL operation failures
        """
        from .issue import Issue
        
        if not self.client:
            raise ValueError("Client must be set to fetch issues")
        
        if not self.owner_login or not self.name:
            raise ValueError("Repository owner_login and name must be set to fetch issues")
            
        query = load_query("get_repository_issues")
        variables = {
            "owner": self.owner_login,
            "repo": self.name,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        issues_data = response["repository"]["issues"]
        
        # Convert each node to an Issue object
        issues_data["nodes"] = [
            Issue.from_response(issue_data, self.client, self.owner_login, self.name) 
            for issue_data in issues_data["nodes"]
        ]
        
        return issues_data
    
    def get_discussions(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get discussions for this repository.
        
        Args:
            first (int, optional): Number of discussions to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of discussion data
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set or owner_login/name are not set
            GraphQLError: On GraphQL operation failures
        """
        if not self.client:
            raise ValueError("Client must be set to fetch discussions")
        
        if not self.owner_login or not self.name:
            raise ValueError("Repository owner_login and name must be set to fetch discussions")
            
        query = load_query("get_repository_discussions")
        variables = {
            "owner": self.owner_login,
            "repo": self.name,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        discussions_data = response["repository"]["discussions"]
        
        return discussions_data
    
    def get_milestones(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get milestones for this repository.
        
        Args:
            first (int, optional): Number of milestones to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of Milestone objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set or owner_login/name are not set
            GraphQLError: On GraphQL operation failures
        """
        from .milestone import Milestone
        
        if not self.client:
            raise ValueError("Client must be set to fetch milestones")
        
        if not self.owner_login or not self.name:
            raise ValueError("Repository owner_login and name must be set to fetch milestones")
            
        query = load_query("get_repository_milestones")
        variables = {
            "owner": self.owner_login,
            "repo": self.name,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        milestones_data = response["repository"]["milestones"]
        
        # Convert each node to a Milestone object
        milestones_data["nodes"] = [
            Milestone(
                id=milestone["id"],
                number=milestone["number"],
                title=milestone["title"],
                state=milestone["state"],
                description=milestone.get("description"),
                due_on=milestone.get("dueOn"),
                created_at=milestone.get("createdAt"),
                closed_at=milestone.get("closedAt"),
                updated_at=milestone.get("updatedAt"),
                url=milestone.get("url"),
                client=self.client
            ) for milestone in milestones_data["nodes"]
        ]
        
        return milestones_data
    
    def get_releases(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get releases for this repository.
        
        Args:
            first (int, optional): Number of releases to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of release data
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set or owner_login/name are not set
            GraphQLError: On GraphQL operation failures
        """
        if not self.client:
            raise ValueError("Client must be set to fetch releases")
        
        if not self.owner_login or not self.name:
            raise ValueError("Repository owner_login and name must be set to fetch releases")
            
        query = load_query("get_repository_releases")
        variables = {
            "owner": self.owner_login,
            "repo": self.name,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        releases_data = response["repository"]["releases"]
        
        return releases_data
