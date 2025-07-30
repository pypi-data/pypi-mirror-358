"""Project View model class."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..client import GraphQLClient
from ..queries import load_query


@dataclass
class View:
    """Represents a view in a GitHub Project (V2)."""

    id: str
    name: str
    number: int = 0
    layout: str = ""
    fields: List[Dict[str, Any]] = None
    client: Optional[GraphQLClient] = None
    project_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values for list fields."""
        if self.fields is None:
            self.fields = []

    @classmethod
    def from_response(cls, data: Dict[str, Any], client: Optional[GraphQLClient] = None, project_id: Optional[str] = None) -> "View":
        """Create a View instance from API response data.

        Args:
            data (Dict[str, Any]): Raw view data from API response
            client (Optional[GraphQLClient]): GraphQL client for API calls
            project_id (Optional[str]): ID of the project this view belongs to

        Returns:
            View: New View instance
        """
        # For node query, data is in ["node"]
        if "node" in data:
            view_data = data["node"]
        else:
            view_data = data
            
        return cls(
            id=view_data["id"],
            name=view_data["name"],
            number=view_data["number"],
            layout=view_data["layout"],
            fields=view_data["fields"]["nodes"],
            client=client,
            project_id=project_id,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        id: Optional[str] = None,
        name: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> "View":
        """Get a view's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            id (Optional[str]): View ID (for lookup by ID)
            name (Optional[str]): View name (for lookup by name, requires project_id)
            project_id (Optional[str]): Project ID (required when looking up by name)
            
        Returns:
            View: Self with populated properties
            
        Raises:
            ValueError: If neither id nor (name and project_id) are provided
            GraphQLError: On GraphQL operation failures
        """
        if not id and not (name and project_id):
            raise ValueError("Either id or (name and project_id) must be provided")
            
        if id:
            query = load_query("get_view")
            variables = {
                "viewId": id,
                "fieldsFirst": 100
            }
            
            response = client.execute(query, variables)
            
            # Use from_response to create a view instance with all properties
            view = View.from_response(response, client)
            
            # Update this instance's attributes with the fetched data
            self.id = view.id
            self.name = view.name
            self.number = view.number
            self.layout = view.layout
            self.fields = view.fields
            self.client = client
            self.project_id = None  # Not returned in the query
            
        else:
            # To find by name, we need to get all views from the project and filter
            query = load_query("get_project_views")
            variables = {
                "projectId": project_id,
                "viewsFirst": 20  # Adjust if needed
            }
            
            response = client.execute(query, variables)
            
            # Find the view with the matching name
            project_views = response["node"]["views"]["nodes"]
            matching_views = [v for v in project_views if v["name"] == name]
            
            if not matching_views:
                raise ValueError(f"No view found with name '{name}' in project")
                
            view_data = matching_views[0]
            
            # We need to fetch the complete view data with the ID
            view_id = view_data["id"]
            return self.get(client=client, id=view_id)
            
        return self
