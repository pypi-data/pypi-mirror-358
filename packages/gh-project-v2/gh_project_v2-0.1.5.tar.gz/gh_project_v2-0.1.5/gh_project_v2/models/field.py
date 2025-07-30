"""Field model classes for GitHub Project fields."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from ..client import GraphQLClient
from ..queries import load_query
from .option import Option


@dataclass
class Field:
    """Represents a field in a GitHub Project (V2)."""

    # Field type constants
    TEXT = "ProjectV2ItemFieldTextValue"
    DATE = "ProjectV2ItemFieldDateValue"
    SINGLE_SELECT = "ProjectV2ItemFieldSingleSelectValue"
    USER = "ProjectV2ItemFieldUserValue"
    REPOSITORY = "ProjectV2ItemFieldRepositoryValue"
    MILESTONE = "ProjectV2ItemFieldMilestoneValue"
    NUMBER = "ProjectV2ItemFieldNumberValue"

    id: str
    name: str
    data_type: str
    type: Optional[str] = None
    value: Optional[Any] = None
    updated: Optional[datetime] = None
    options: Optional[List[Option]] = None
    client: Optional[GraphQLClient] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any], client: Optional[GraphQLClient] = None) -> "Field":
        """Create a Field instance from API response data.

        Args:
            data (Dict[str, Any]): Raw field data from API response
            client (Optional[GraphQLClient]): GraphQL client for API calls

        Returns:
            Field: New Field instance
        """
        options = None

        # If this is a single select field and has options, create Option objects
        if data.get("dataType") == "SINGLE_SELECT" and "options" in data:
            options_data = data.get("options", [])
            options = [Option.from_response(option, client) for option in options_data]

        # Set value and updated if they exist in the data
        value = data.get("value")
        updated = None
        if "updatedAt" in data:
            updated = datetime.fromisoformat(data["updatedAt"].replace("Z", "+00:00"))

        return cls(
            id=data.get("id"),
            name=data.get("name"),
            data_type=data.get("dataType"),
            type=data.get("type"),
            value=value,
            updated=updated,
            options=options,
            client=client
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        id: str
    ) -> "Field":
        """Get a field's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            id (str): Field node ID
            
        Returns:
            Field: Self with populated properties
            
        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_field")
        variables = {
            "id": id
        }
        
        response = client.execute(query, variables)
        
        # Use from_response to create a field instance with all properties
        field = Field.from_response(response["node"], client)
        
        # Update this instance's attributes with the fetched data
        self.id = field.id
        self.name = field.name
        self.data_type = field.data_type
        self.type = field.type
        self.value = field.value
        self.updated = field.updated
        self.options = field.options
        self.client = client
        
        return self
