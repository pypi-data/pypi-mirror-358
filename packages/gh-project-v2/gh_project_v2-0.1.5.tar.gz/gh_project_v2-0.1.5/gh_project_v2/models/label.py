"""Models representing GitHub Labels."""

from dataclasses import dataclass
from typing import Optional, Union, List
from datetime import datetime

from ..client import GraphQLClient
from ..queries import load_query
from .utils import parse_datetime

@dataclass
class Label:
    """Represents a GitHub label."""

    id: str = ""
    name: str = ""
    color: str = ""
    description: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_default: bool = False
    client: Optional[GraphQLClient] = None

    """Initialize a new Label.

    Args:
        id (str): The GitHub node ID
        name (str): The label name
        color (str): The hex color code without #
        description (Optional[str]): Label description text
        url (Optional[str]): URL to view the label
        created_at (Optional[datetime]): Creation timestamp
        updated_at (Optional[datetime]): Last update timestamp
        is_default (bool): Whether this is a default label
        client (Optional[GraphQLClient]): GraphQL client for API calls
    """

    @classmethod
    def from_response(cls, response: dict, client: Optional[GraphQLClient] = None) -> Optional["Label"]:
        """Create a Label from a GraphQL response.

        Args:
            response (dict): The GraphQL response data
            client (Optional[GraphQLClient]): GraphQL client for API calls

        Returns:
            Optional[Label]: A Label object, or None if invalid data
        """
        repo_data = response.get("repository", {})
        label_data = repo_data.get("label")

        if not label_data:
            # Check if this is a node response (for label by ID)
            node_data = response.get("node")
            if node_data:
                label_data = node_data
            else:
                return None

        return cls(
            id=label_data["id"],
            name=label_data["name"],
            color=label_data["color"],
            description=label_data.get("description"),
            url=label_data.get("url"),
            created_at=parse_datetime(label_data.get("createdAt")),
            updated_at=parse_datetime(label_data.get("updatedAt")),
            is_default=label_data.get("isDefault", False),
            client=client,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        repository: str,
        name: Optional[str] = None,
        id: Optional[str] = None,
        owner: Optional[str] = None
    ) -> "Label":
        """Get a label's details and populate this instance.
        
        If name is provided, get all labels on the repo and search for one that matches.
        If id is provided, query directly for the Label with that ID.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            repository (str): Repository name
            name (Optional[str]): Label name
            id (Optional[str]): Label node ID
            owner (Optional[str]): Repository owner (user or organization)
            
        Returns:
            Label: Self with populated properties
            
        Raises:
            ValueError: If neither name nor id is provided, or if owner is missing when using name
            ValueError: If label with provided name is not found
            GraphQLError: On GraphQL operation failures
        """
        if not name and not id:
            raise ValueError("Either name or id must be provided")
            
        self.client = client
        
        if id:
            # Get label by ID
            query = load_query("get_label_by_id")
            variables = {"id": id}
            
            response = client.execute(query, variables)
            label = Label.from_response(response, client)
            
            if not label:
                raise ValueError(f"Label with ID {id} not found")
        else:
            # Get label by name
            if not owner:
                raise ValueError("Owner is required when getting label by name")
                
            query = load_query("get_label")
            variables = {
                "owner": owner,
                "repo": repository,
                "name": name
            }
            
            response = client.execute(query, variables)
            label = Label.from_response(response, client)
            
            if not label:
                raise ValueError(f"Label '{name}' not found in {owner}/{repository}")
        
        # Update this instance's attributes with the fetched data
        self.id = label.id
        self.name = label.name
        self.color = label.color
        self.description = label.description
        self.url = label.url
        self.created_at = label.created_at
        self.updated_at = label.updated_at
        self.is_default = label.is_default
        
        return self