"""Project model class."""

from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
from ..client import GraphQLClient
from ..clients import _paginate_query
from ..queries import load_query
from .issue import Issue
from .view import View
from .repository import Repository
from .team import Team
from .workflow import Workflow
from .user import User
from .organization import Organization

if TYPE_CHECKING:
    from .field import Field
    from .draft_issue import DraftIssue
    from .pull_request import PullRequest


@dataclass
class Project:
    """Represents a GitHub Project (V2) with its properties and methods."""

    id: str = ""
    title: str = ""
    short_description: Optional[str] = None
    public: bool = False
    closed: bool = False
    url: str = ""
    number: int = 0
    creator: Optional[Union[User, Organization]] = None
    owner: Optional[Union[User, Organization]] = None
    readme: Optional[str] = None
    updated_at: Optional[datetime] = None
    resource_path: Optional[str] = None
    client: Optional[GraphQLClient] = None

    @classmethod
    def from_response(cls, data: Dict[str, Any], client: GraphQLClient) -> "Project":
        """Create a Project instance from API response data.

        Args:
            data (Dict[str, Any]): Raw project data from API response
            client (GraphQLClient): GraphQL client for API calls

        Returns:
            Project: New Project instance
        """
        from .utils import parse_datetime

        # Get the project data - could be under user or organization key
        owner_data = data.get("user") or data.get("organization", {})
        project_data = owner_data.get("projectV2", {})

        # Parse creator field
        creator = None
        if project_data.get("creator"):
            creator_data = project_data["creator"]
            if (
                creator_data.get("__typename") == "Organization"
                or "organization" in creator_data
            ):
                creator = Organization.from_response(
                    {"organization": creator_data}, client
                )
            else:
                creator = User.from_response({"user": creator_data}, client)

        # Parse owner field
        owner = None
        if project_data.get("owner"):
            owner_data = project_data["owner"]
            
            if (
                owner_data.get("__typename") == "Organization"
                or "organization" in owner_data
            ):
                owner = Organization.from_response({"organization": owner_data}, client)
            else:
                owner = User.from_response({"user": owner_data}, client)

        return cls(
            id=project_data.get("id"),
            title=project_data.get("title"),
            short_description=project_data.get("shortDescription"),
            public=project_data.get("public", False),
            closed=project_data.get("closed", False),
            url=project_data.get("url"),
            number=project_data.get("number"),
            creator=creator,
            owner=owner,
            readme=project_data.get("readme"),
            updated_at=parse_datetime(project_data.get("updatedAt")),
            resource_path=project_data.get("resourcePath"),
            client=client,
        )

    def get(self, *, client: GraphQLClient, owner: str, number: int) -> "Project":
        """Get a project's details and populate this instance.

        Args:
            client (GraphQLClient): GraphQL client for API calls
            owner (str): Project owner (organization or username)
            number (int): Project number

        Returns:
            Project: Self with populated properties

        Raises:
            GraphQLError: On GraphQL operation failures
        """
        from gh_project_v2.projects_v2 import ProjectsV2Client

        projects_client = ProjectsV2Client(client)
        project = projects_client.get_project(number, owner)

        # Update this instance's attributes with the fetched data
        self.id = project.id
        self.title = project.title
        self.short_description = project.short_description
        self.public = project.public
        self.closed = project.closed
        self.url = project.url
        self.number = project.number
        self.creator = project.creator
        self.owner = project.owner
        self.readme = project.readme
        self.updated_at = project.updated_at
        self.resource_path = project.resource_path
        self.client = client

        return self

    # Removed duplicate _paginate_query method - now using the one from clients.py

    def get_fields(self, first: int = 20) -> List["Field"]:
        """Get fields configured in this project.

        This method is deprecated. Use ProjectsV2Client.list_project_fields instead.

        Args:
            first (int, optional): Number of items per page. Defaults to 20.

        Returns:
            List[Field]: List of project field objects
        """
        from gh_project_v2.projects_v2 import ProjectsV2Client

        projects_client = ProjectsV2Client(self.client)
        return projects_client.list_project_fields(self.id, first)

    def find_field_by_name(
        self, name: str, fields: Optional[List["Field"]] = None
    ) -> Optional["Field"]:
        """Search for a field by name in this project.

        Args:
            name (str): The name of the field to search for
            fields (Optional[List["Field"]], optional): List of fields to search in.
                If None, will fetch fields from the project. Defaults to None.

        Returns:
            Optional["Field"]: Matching field or None if not found
        """
        if fields is None:
            from gh_project_v2.projects_v2 import ProjectsV2Client

            projects_client = ProjectsV2Client(self.client)
            fields = projects_client.list_project_fields(self.id)

        for field in fields:
            if field.name == name:
                return field

        return None

    def get_items(
        self, first: int = 20, fields_first: Optional[int] = None, users_first: int = 20
    ) -> List[Union["Issue", "DraftIssue", "PullRequest"]]:
        """Get items (issues/PRs/draft issues) in this project.

        Args:
            first (int, optional): Number of items per page. Defaults to 20.
            fields_first (int, optional): Number of field values per page. Default None.
                A value between 1 and 100 must be provided if set.
            users_first (int, optional): Number of users per field value page. Defaults to 20.

        Returns:
            List[Union[Issue, DraftIssue, PullRequest]]: List of project item objects
                from the API

        Raises:
            ValueError: If fields_first is greater than 100 or less than 1
        """
        if fields_first is not None:
            if not 1 <= fields_first <= 100:
                raise ValueError("fields_first must be between 1 and 100")

        query = load_query("get_project_issues")
        variables = {"projectId": self.id, "first": first, "usersFirst": users_first}
        if fields_first is not None:
            variables["fieldsFirst"] = fields_first
            response = _paginate_query(
                self.client, query, variables, "node.items", nested_path="fieldValues"
            )
        else:
            response = _paginate_query(self.client, query, variables, "node.items")
        items_data = response["node"]["items"]

        from .draft_issue import DraftIssue
        from .issue import Issue
        from .pull_request import PullRequest

        items = []
        for node in items_data["nodes"]:
            item_type = node["content"].get("__typename")
            if item_type == "PullRequest":
                items.append(PullRequest.from_response(node, self.client))
            elif item_type == "DraftIssue":
                items.append(DraftIssue.from_response(node, self.client))
            else:  # Default to Issue for backward compatibility
                items.append(Issue.from_response(node, self.client))

        return items

    def get_views(
        self, first: int = 20, fields_first: Optional[int] = None
    ) -> List[View]:
        """Get views configured in this project.

        Args:
            first (int, optional): Number of views to fetch per page. Defaults to 20.
            fields_first (int, optional): Number of fields per page. Defaults to 20.
                A value between 1 and 100 must be provided if set.

        Returns:
            List[View]: List of project views as View objects

        Raises:
            ValueError: If fields_first is greater than 100 or less than 1
        """
        if fields_first is not None:
            if not 1 <= fields_first <= 100:
                raise ValueError("fields_first must be between 1 and 100")

        query = load_query("get_project_views")
        variables = {"projectId": self.id, "first": first}
        if fields_first is not None:
            variables["fieldsFirst"] = fields_first
            response = _paginate_query(
                self.client, query, variables, "node.views", nested_path="fields"
            )
        else:
            response = _paginate_query(self.client, query, variables, "node.views")
        raw_views = response["node"]["views"]
        return [View.from_response(node, self.client) for node in raw_views["nodes"]]

    def get_repositories(self, first: int = 20) -> List[Repository]:
        """Get repositories linked to this project.

        Args:
            first (int, optional): Number of repositories to fetch per page.
                Defaults to 20.

        Returns:
            List[Repository]: List of Repository instances with data from the API
        """
        query = load_query("get_project_repositories")
        variables = {"projectId": self.id, "first": first}
        response = _paginate_query(self.client, query, variables, "node.repositories")

        repositories_data = response["node"]["repositories"]
        return [
            Repository.from_response({"repository": node}, self.client)
            for node in repositories_data["nodes"]
        ]

    def get_teams(self, first: int = 20) -> List[Team]:
        """Get teams linked to this project.

        Args:
            first (int, optional): Number of teams to fetch per page. Defaults to 20.

        Returns:
            List[Team]: List of Team instances with data from the API
        """
        query = load_query("get_project_teams")
        variables = {"projectId": self.id, "first": first}
        response = _paginate_query(self.client, query, variables, "node.teams")

        teams_data = response["node"]["teams"]
        return [
            Team.from_response({"team": node}, self.client)
            for node in teams_data["nodes"]
        ]

    def get_workflows(self, first: int = 20) -> List[Workflow]:
        """Get workflows linked to this project.

        Args:
            first (int, optional): Number of workflows to fetch per page.
                Defaults to 20.

        Returns:
            List[Workflow]: List of Workflow instances with data from the API
        """
        query = load_query("get_project_workflows")
        variables = {"projectId": self.id, "first": first}
        response = _paginate_query(self.client, query, variables, "node.workflows")

        workflows_data = response["node"]["workflows"]
        return [
            Workflow.from_response({"workflow": node}, self.client)
            for node in workflows_data["nodes"]
        ]
