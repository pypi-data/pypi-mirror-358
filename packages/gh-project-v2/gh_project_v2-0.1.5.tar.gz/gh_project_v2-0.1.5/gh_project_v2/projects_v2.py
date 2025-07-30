"""GitHub Projects V2 API client implementation."""

from .client import GraphQLClient
from .queries import env, load_query
from .models.project import Project
from .models.user import User
from .models.label import Label
from .models.milestone import Milestone
from .models.organization import Organization
from .models.repository import Repository
from typing import Any, Union, List, TYPE_CHECKING
from .clients import _paginate_query, SearchType

if TYPE_CHECKING:
    from .models.issue import Issue
    from .models.field import Field


class ProjectsV2Client:
    """Client for interacting with GitHub's ProjectsV2 API."""

    def __init__(self, client_or_token: Union[GraphQLClient, str], api_url: str = "https://api.github.com/graphql"):
        """Initialize the ProjectsV2 client.

        Args:
            client_or_token (Union[GraphQLClient, str]): Either an authenticated GraphQL client instance 
                                                       or a GitHub Personal Access Token string
            api_url (str, optional): GitHub GraphQL API endpoint. Only used when client_or_token is a token string.
                                   Defaults to "https://api.github.com/graphql".
        
        Raises:
            ValueError: If client_or_token is None or invalid
        """
        if client_or_token is None:
            raise ValueError(
                "client_or_token cannot be None. Please provide either a GitHub Personal Access Token "
                "string or a GraphQLClient instance. If using an environment variable, ensure it is set."
            )
        
        if isinstance(client_or_token, str):
            if not client_or_token.strip():
                raise ValueError(
                    "Token cannot be empty. Please provide a valid GitHub Personal Access Token."
                )
            # Create GraphQLClient internally when token string is provided
            self.client = GraphQLClient(client_or_token, api_url)
        else:
            # Use provided GraphQLClient instance
            self.client = client_or_token

    def get_project(
        self, project_number: int, owner: str, owner_type: str = "user"
    ) -> Project:
        """Get a ProjectV2 by number.

        Args:
            project_number (int): The number of the project
            owner (str): The login of the project owner
            owner_type (str, optional): Type of owner - "user" or "org".
                                      Defaults to "user".

        Returns:
            Project: Project object containing the API data and methods

        Raises:
            ValueError: If owner_type is not "user" or "org"
        """
        if owner_type not in ["user", "org"]:
            raise ValueError('owner_type must be either "user" or "org"')

        # Render the query template with the owner_type context
        tmpl_name = "get_project.graphql"
        query = env.get_template(tmpl_name).render(owner_type=owner_type)

        variables = {"owner": owner, "number": project_number}
        response = self.client.execute(query, variables)

        # Transform response to have consistent structure
        formatted_response = {}
        if owner_type == "user" and response.get("user", {}).get("projectV2"):
            formatted_response = {"user": response["user"]}
        elif owner_type == "org" and response.get("organization", {}).get("projectV2"):
            formatted_response = {"user": response["organization"]}
        else:
            formatted_response = response

        return Project.from_response(formatted_response, self.client)

    def get_user(self, login: str) -> User:
        """Get information about a GitHub user.

        Args:
            login (str): GitHub username to fetch

        Returns:
            User: User object with profile information

        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_user")
        variables = {"login": login}
        response = self.client.execute(query, variables)
        return User.from_response(response)

    def get_issue(self, owner: str, repo: str, number: int) -> "Issue":
        """Get a specific issue by its repository and number.

        Args:
            owner (str): Repository owner (user or organization)
            repo (str): Repository name
            number (int): Issue number

        Returns:
            Issue: Issue object

        Raises:
            GraphQLError: On GraphQL operation failures
        """
        from .models.issue import Issue  # Lazy import

        query = load_query("get_issue")
        variables = {"owner": owner, "repo": repo, "number": number}
        response = self.client.execute(query, variables)
        return Issue.from_response(response, self.client, owner, repo)

    def get_organization(self, login: str) -> Organization:
        """Get information about a GitHub organization.

        Args:
            login (str): The organization's login/name

        Returns:
            Organization: Organization object with the fetched data

        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_organization")
        variables = {"login": login}
        response = self.client.execute(query, variables)
        return Organization.from_response(response)

    def get_repository(self, owner: str, name: str) -> Repository:
        """Get information about a GitHub repository.

        Args:
            owner (str): The repository owner's login (user or organization)
            name (str): The repository name

        Returns:
            Repository: Repository object with the fetched data

        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_repository")
        variables = {"owner": owner, "name": name}
        response = self.client.execute(query, variables)
        return Repository.from_response(response, self.client)

    def get_milestone(self, owner: str, repo: str, number: int) -> Milestone:
        """Get a specific milestone by its repository and number.

        Args:
            owner (str): Repository owner (user or organization)
            repo (str): Repository name
            number (int): Milestone number

        Returns:
            Milestone: Milestone object with the fetched data

        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_milestone")
        variables = {"owner": owner, "repo": repo, "number": number}
        response = self.client.execute(query, variables)
        return Milestone.from_response(response)

    def get_label(self, owner: str, repo: str, name: str) -> Label:
        """Get a specific label by its repository and name.

        Args:
            owner (str): Repository owner (user or organization)
            repo (str): Repository name
            name (str): Label name

        Returns:
            Label: Label object with the fetched data

        Raises:
            GraphQLError: On GraphQL operation failures
        """
        query = load_query("get_label")
        variables = {"owner": owner, "repo": repo, "name": name}
        response = self.client.execute(query, variables)
        return Label.from_response(response, self.client)

    def list_project_fields(self, project_id: str, first: int = 20) -> List["Field"]:
        """Get fields configured in a project.

        Args:
            project_id (str): The node ID of the project
            first (int, optional): Number of items per page. Defaults to 20.

        Returns:
            List[Field]: List of project field objects
        """
        from .models.field import Field  # Avoid circular import

        query = load_query("list_project_fields")
        variables = {"projectId": project_id, "first": first}
        result = _paginate_query(self.client, query, variables, "node.fields")
        field_nodes = result["node"]["fields"]["nodes"]
        
        # Convert raw field data to Field objects
        return [Field.from_response(field_data) for field_data in field_nodes]

    def search(
        self,
        query: str,
        search_type: Union[SearchType, str],
        first: int = 20,
        after: str = None,
    ) -> List[Any]:
        """Search GitHub using the GraphQL API.

        Args:
            query (str): Search query string (see GitHub's search syntax)
            search_type (Union[SearchType, str]): Type of items to search for
            first (int, optional): Number of results per page. Defaults to 20.
            after (str, optional): Cursor for pagination. Defaults to None.

        Returns:
            List[Any]: List of search result objects based on the search_type

        Raises:
            GraphQLError: On GraphQL operation failures
        """
        from .models.issue import Issue  # Lazy import
        from .models.pull_request import PullRequest  # Lazy import
        from .models.draft_issue import DraftIssue  # Lazy import
        from .models.repository import Repository  # Lazy import

        # Convert string type to enum if needed
        if isinstance(search_type, str):
            search_type = SearchType(search_type.upper())

        variables = {
            "query": query,
            "type": search_type,
            "first": first
        }
        if after:
            variables["after"] = after

        gql_query = load_query("search")
        response = _paginate_query(self.client, gql_query, variables, "search")
        nodes = response["search"]["nodes"]
        result = []

        # Transform nodes to appropriate type based on search_type
        for node in nodes:
            if search_type == SearchType.ISSUE:
                if node["__typename"] == "Issue":
                    owner, repo = node["repository"]["nameWithOwner"].split("/")
                    result.append(Issue.from_response(
                        {"node": node}, self.client, owner, repo))
                elif node["__typename"] == "PullRequest":
                    owner, repo = node["repository"]["nameWithOwner"].split("/")
                    result.append(PullRequest.from_response(
                        {"node": node}, self.client, owner, repo))
                elif node["__typename"] == "DraftIssue":
                    owner, repo = node["repository"]["nameWithOwner"].split("/")
                    result.append(DraftIssue.from_response(
                        {"node": node}, self.client, owner, repo))
            elif search_type == SearchType.REPOSITORY:
                if node["__typename"] == "Repository":
                    # Adapt node format to match what Repository.from_response expects
                    result.append(Repository.from_response({"repository": node}, self.client))
            else:
                # For unhandled types, append the raw node
                result.append(node)
        return result
