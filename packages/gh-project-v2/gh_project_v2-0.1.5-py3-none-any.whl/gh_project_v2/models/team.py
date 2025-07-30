"""Team model class for GitHub API responses."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from ..client import GraphQLClient
from ..queries import load_query


@dataclass(eq=True, frozen=True)
class Team:
    """Represents a GitHub team."""

    id: str
    name: str
    slug: str
    description: Optional[str] = None
    url: str = ""
    privacy: str = ""
    members_count: int = 0
    repositories_count: int = 0
    client: Optional[GraphQLClient] = None

    def __hash__(self):
        """Make Team hashable by its id."""
        return hash(self.id)

    @classmethod
    def from_response(cls, data: Dict[str, Any], client: Optional[GraphQLClient] = None) -> "Team":
        """Create Team instance from GraphQL response.

        Args:
            data (Dict[str, Any]): GraphQL response data containing team info
            client (Optional[GraphQLClient], optional): GraphQL client for API calls. Defaults to None.

        Returns:
            Team: New Team instance
        """
        team_data = data.get("node", data.get("team", {}))
        
        return cls(
            id=team_data.get("id", ""),
            name=team_data.get("name", ""),
            slug=team_data.get("slug", ""),
            description=team_data.get("description"),
            url=team_data.get("url", ""),
            privacy=team_data.get("privacy", ""),
            members_count=team_data.get("membersCount", 0),
            repositories_count=team_data.get("repositoriesCount", 0),
            client=client,
        )
        
    def get(
        self,
        *,
        client: GraphQLClient,
        org: str,
        slug: str
    ) -> "Team":
        """Get a team's details and populate this instance.
        
        Args:
            client (GraphQLClient): GraphQL client for API calls
            org (str): Organization name
            slug (str): Team slug
            
        Returns:
            Team: Self with populated properties
            
        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_team")
        variables = {
            "org": org,
            "slug": slug
        }
        
        response = client.execute(query, variables)
        
        # Use from_response to create a team instance with all properties
        team = Team.from_response(response["organization"], client)
        
        # Update this instance's attributes with the fetched data
        object.__setattr__(self, "id", team.id)
        object.__setattr__(self, "name", team.name)
        object.__setattr__(self, "slug", team.slug)
        object.__setattr__(self, "description", team.description)
        object.__setattr__(self, "url", team.url)
        object.__setattr__(self, "privacy", team.privacy)
        object.__setattr__(self, "members_count", team.members_count)
        object.__setattr__(self, "repositories_count", team.repositories_count)
        object.__setattr__(self, "client", client)
        
        return self