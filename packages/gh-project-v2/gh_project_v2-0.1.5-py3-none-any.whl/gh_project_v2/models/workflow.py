"""Workflow model class for GitHub API responses."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from ..client import GraphQLClient
from ..queries import load_query


@dataclass(eq=True, frozen=True)
class Workflow:
    """Represents a GitHub workflow."""

    id: str
    name: str
    path: str
    state: str
    url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    file_contents: Optional[str] = None
    ref: Optional[str] = None
    run_count: int = 0
    client: Optional[GraphQLClient] = None

    def __hash__(self):
        """Make Workflow hashable by its id."""
        return hash(self.id)

    @classmethod
    def from_response(cls, data: Dict[str, Any], client: Optional[GraphQLClient] = None) -> "Workflow":
        """Create Workflow instance from GraphQL response.

        Args:
            data (Dict[str, Any]): GraphQL response data containing workflow info
            client (Optional[GraphQLClient], optional): GraphQL client for API calls. Defaults to None.

        Returns:
            Workflow: New Workflow instance
        """
        workflow_data = data.get("node", data.get("workflow", {}))
        
        return cls(
            id=workflow_data.get("id", ""),
            name=workflow_data.get("name", ""),
            path=workflow_data.get("path", ""),
            state=workflow_data.get("state", ""),
            url=workflow_data.get("url"),
            created_at=workflow_data.get("createdAt"),
            updated_at=workflow_data.get("updatedAt"),
            file_contents=workflow_data.get("fileContents"),
            ref=workflow_data.get("ref"),
            run_count=workflow_data.get("runCount", 0),
            client=client,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        id: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None
    ) -> "Workflow":
        """Get a workflow's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            id (str): Workflow node ID
            owner (Optional[str]): Repository owner (organization or username)
            repo (Optional[str]): Repository name
            
        Returns:
            Workflow: Self with populated properties
            
        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_workflow")
        variables = {
            "id": id,
            "owner": owner or "",
            "repo": repo or ""
        }
        
        response = client.execute(query, variables)
        
        # Use from_response to create a workflow instance with all properties
        workflow = Workflow.from_response(response, client)
        
        # Update this instance's attributes with the fetched data
        object.__setattr__(self, "id", workflow.id)
        object.__setattr__(self, "name", workflow.name)
        object.__setattr__(self, "path", workflow.path)
        object.__setattr__(self, "state", workflow.state)
        object.__setattr__(self, "url", workflow.url)
        object.__setattr__(self, "created_at", workflow.created_at)
        object.__setattr__(self, "updated_at", workflow.updated_at)
        object.__setattr__(self, "file_contents", workflow.file_contents)
        object.__setattr__(self, "ref", workflow.ref)
        object.__setattr__(self, "run_count", workflow.run_count)
        object.__setattr__(self, "client", client)
        
        return self