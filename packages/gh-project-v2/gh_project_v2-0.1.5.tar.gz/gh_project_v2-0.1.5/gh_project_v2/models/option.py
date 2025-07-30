"""Option model class for GitHub Project field options."""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..client import GraphQLClient
from ..queries import load_query


@dataclass
class Option:
    """Represents an option in a single select field in a GitHub Project (V2)."""

    id: str
    name: str
    client: Optional[GraphQLClient] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any], client: Optional[GraphQLClient] = None) -> "Option":
        """Create an Option instance from API response data.

        Args:
            data (Dict[str, Any]): Raw option data from API response
            client (Optional[GraphQLClient]): GraphQL client for API calls

        Returns:
            Option: New Option instance
        """
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            client=client
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        id: str
    ) -> "Option":
        """Get an option's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            id (str): Option node ID
            
        Returns:
            Option: Self with populated properties
            
        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_option")
        variables = {
            "id": id
        }
        
        response = client.execute(query, variables)
        
        # Use from_response to create an option instance with all properties
        option = Option.from_response(response["node"], client)
        
        # Update this instance's attributes with the fetched data
        self.id = option.id
        self.name = option.name
        self.client = client
        
        return self