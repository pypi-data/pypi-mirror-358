"""Models representing GitHub Milestones."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

from ..client import GraphQLClient
from ..queries import load_query
from .utils import parse_datetime

@dataclass
class Milestone:
    """Represents a GitHub milestone."""

    id: str
    number: int
    title: str
    state: str
    description: Optional[str] = None
    due_on: Optional[datetime] = None
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    url: Optional[str] = None
    client: Optional[GraphQLClient] = None

    """Initialize a new Milestone.

    Args:
        id (str): The GitHub node ID
        number (int): The milestone number
        title (str): The milestone title
        state (str): Current state (OPEN or CLOSED)
        description (Optional[str]): Description text
        due_on (Optional[datetime]): Due date if set
        created_at (Optional[datetime]): Creation timestamp
        closed_at (Optional[datetime]): Close timestamp if closed
        updated_at (Optional[datetime]): Last update timestamp
        url (Optional[str]): URL to view the milestone
        client (Optional[GraphQLClient]): GraphQL client for API calls
    """

    @classmethod
    def from_response(cls, response: dict, client: Optional[GraphQLClient] = None) -> Optional["Milestone"]:
        """Create a Milestone from a GraphQL response.

        Args:
            response (dict): The GraphQL response data
            client (Optional[GraphQLClient]): GraphQL client for API calls

        Returns:
            Optional[Milestone]: A Milestone object or None if not found
        """
        repo_data = response.get("repository", {})
        milestone_data = repo_data.get("milestone")

        if not milestone_data:
            return None

        return cls(
            id=milestone_data["id"],
            number=milestone_data["number"],
            title=milestone_data["title"],
            state=milestone_data["state"],
            description=milestone_data.get("description"),
            due_on=parse_datetime(milestone_data.get("dueOn")),
            created_at=parse_datetime(milestone_data.get("createdAt")),
            closed_at=parse_datetime(milestone_data.get("closedAt")),
            updated_at=parse_datetime(milestone_data.get("updatedAt")),
            url=milestone_data.get("url"),
            client=client,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        owner: str,
        repo: str,
        number: int
    ) -> Optional["Milestone"]:
        """Get a milestone's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            owner (str): Repository owner (organization or username)
            repo (str): Repository name
            number (int): Milestone number
            
        Returns:
            Optional[Milestone]: Self with populated properties or None if not found
            
        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_milestone")
        variables = {
            "owner": owner,
            "repo": repo,
            "number": number
        }
        
        response = client.execute(query, variables)
        
        # Use from_response to create a milestone instance with all properties
        milestone = Milestone.from_response(response, client)
        
        if milestone is None:
            return None
            
        # Update this instance's attributes with the fetched data
        self.id = milestone.id
        self.number = milestone.number
        self.title = milestone.title
        self.state = milestone.state
        self.description = milestone.description
        self.due_on = milestone.due_on
        self.created_at = milestone.created_at
        self.closed_at = milestone.closed_at
        self.updated_at = milestone.updated_at
        self.url = milestone.url
        self.client = client
        
        return self
        
    def get_issues(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get issues for this milestone.
        
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
            raise ValueError("Client must be set to fetch milestone issues")
            
        # Extract owner and repo from URL
        # URL format: https://github.com/owner/repo/milestone/number
        url_parts = self.url.split('/')
        if len(url_parts) < 5 or url_parts[2] != 'github.com':
            raise ValueError("Invalid milestone URL format")
            
        owner = url_parts[3]
        repo = url_parts[4]
            
        query = load_query("get_milestone_issues")
        variables = {
            "owner": owner,
            "repo": repo,
            "number": self.number,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        issues_data = response["repository"]["milestone"]["issues"]
        
        # Convert each node to an Issue object
        issues_data["nodes"] = [
            Issue.from_response(issue_data, self.client, owner, repo) 
            for issue_data in issues_data["nodes"]
        ]
        
        return issues_data
        
    def get_pull_requests(self, first: int = 20, after: Optional[str] = None) -> Dict[str, Any]:
        """Get pull requests for this milestone.
        
        Args:
            first (int, optional): Number of pull requests to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - "nodes": List of PullRequest objects
                - "pageInfo": PageInfo object with hasNextPage and endCursor
                
        Raises:
            ValueError: If client is not set
            GraphQLError: On GraphQL operation failures
        """
        from .pull_request import PullRequest
        
        if not self.client:
            raise ValueError("Client must be set to fetch milestone pull requests")
            
        # Extract owner and repo from URL
        # URL format: https://github.com/owner/repo/milestone/number
        url_parts = self.url.split('/')
        if len(url_parts) < 5 or url_parts[2] != 'github.com':
            raise ValueError("Invalid milestone URL format")
            
        owner = url_parts[3]
        repo = url_parts[4]
            
        query = load_query("get_milestone_pull_requests")
        variables = {
            "owner": owner,
            "repo": repo,
            "number": self.number,
            "first": first
        }
        
        if after:
            variables["after"] = after
            
        response = self.client.execute(query, variables)
        prs_data = response["repository"]["milestone"]["pullRequests"]
        
        # Convert each node to a PullRequest object
        prs_data["nodes"] = [
            PullRequest.from_response(pr, self.client, owner, repo) 
            for pr in prs_data["nodes"]
        ]
        
        return prs_data
        
    def get_repo(self) -> Optional["Repository"]:
        """Get the repository associated with this milestone.
        
        Returns:
            Optional[Repository]: Repository object or None if not found
            
        Raises:
            ValueError: If client is not set
            GraphQLError: On GraphQL operation failures
        """
        from .repository import Repository
        
        if not self.client:
            raise ValueError("Client must be set to fetch milestone repository")
            
        # Extract owner and repo from URL
        # URL format: https://github.com/owner/repo/milestone/number
        url_parts = self.url.split('/')
        if len(url_parts) < 5 or url_parts[2] != 'github.com':
            raise ValueError("Invalid milestone URL format")
            
        owner = url_parts[3]
        repo = url_parts[4]
            
        query = load_query("get_milestone_repository")
        variables = {
            "owner": owner,
            "repo": repo,
            "number": self.number
        }
        
        response = self.client.execute(query, variables)
        
        milestone_data = response.get("repository", {}).get("milestone")
        if not milestone_data:
            return None
            
        repo_data = milestone_data.get("repository")
        if not repo_data:
            return None
            
        owner_data = repo_data.get("owner", {})
            
        return Repository(
            id=repo_data["id"],
            name=repo_data["name"],
            name_with_owner=repo_data["nameWithOwner"],
            url=repo_data["url"],
            owner_login=owner_data["login"],
            owner_url=owner_data["url"],
            description=repo_data.get("description"),
            is_private=repo_data.get("isPrivate", False),
            homepage_url=repo_data.get("homepageUrl"),
            client=self.client
        )