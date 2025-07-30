"""Project Issue model class."""

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
from ..client import GraphQLClient
from ..queries import load_query
from .comment import Comment
from .events import Event
from .field import Field
from .label import Label
from .user import User

if TYPE_CHECKING:
    from .organization import Organization
    from .repository import Repository


@dataclass
class Issue:
    """Represents an issue or pull request in a GitHub Project (V2)."""

    id: str = ""
    number: int = 0
    title: str = ""
    url: str = ""
    state: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    field_values: List[Dict[str, Any]] = None
    author_login: str = ""
    body: Optional[str] = None
    client: Optional[GraphQLClient] = None
    owner: Optional[str] = None
    repo: Optional[str] = None
    # New fields from the enhancement
    repository: Optional["Repository"] = None
    issue_owner: Optional[Union[User, "Organization"]] = None
    labels: List[Label] = None
    closed: bool = False
    closed_at: Optional[datetime] = None
    assignees: List[Union[User, "Organization"]] = None

    def __post_init__(self):
        """Initialize default values for list fields."""
        if self.field_values is None:
            self.field_values = []
        if self.labels is None:
            self.labels = []
        if self.assignees is None:
            self.assignees = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def __hash__(self):
        """Make Issue hashable based on its id."""
        return hash(self.id)

    def __eq__(self, other):
        """Compare Issues based on their id."""
        if not isinstance(other, Issue):
            return False
        return self.id == other.id

    @classmethod
    def _parse_repository(cls, repo_data: Dict[str, Any]) -> Optional["Repository"]:
        """Parse repository data from API response."""
        if not repo_data:
            return None

        from .repository import Repository

        return Repository(
            id=repo_data.get("id", ""),
            name=repo_data.get("name", ""),
            name_with_owner=repo_data.get("nameWithOwner", ""),
            url=repo_data.get("url", ""),
            owner_login=repo_data.get("owner", {}).get("login", ""),
            owner_url=repo_data.get("owner", {}).get("url", ""),
            description=repo_data.get("description"),
            is_private=repo_data.get("isPrivate", False),
            homepage_url=repo_data.get("homepageUrl"),
        )

    @classmethod
    def _parse_owner_or_assignee(
        cls, user_data: Dict[str, Any]
    ) -> Union[User, "Organization"]:
        """Parse user or organization data from API response."""
        typename = user_data.get("__typename", "")

        if typename == "Organization":
            from .organization import Organization

            return Organization(
                id=user_data.get("id", ""),
                login=user_data.get("login", ""),
                name=user_data.get("name"),
                description=user_data.get("description"),
                url=user_data.get("url"),
                location=user_data.get("location"),
                website_url=user_data.get("websiteUrl"),
            )
        else:  # Default to User
            return User(
                id=user_data.get("id", ""),
                login=user_data.get("login", ""),
                name=user_data.get("name"),
                email=user_data.get("email"),
                bio=user_data.get("bio"),
                company=user_data.get("company"),
                location=user_data.get("location"),
                website_url=user_data.get("websiteUrl"),
                url=user_data.get("url", ""),
                avatar_url=user_data.get("avatarUrl", ""),
            )

    @classmethod
    def _parse_labels(cls, labels_data: Dict[str, Any]) -> List[Label]:
        """Parse labels data from API response."""
        if not labels_data or "nodes" not in labels_data:
            return []

        labels = []
        for label_data in labels_data["nodes"]:
            labels.append(
                Label(
                    id=label_data["id"],
                    name=label_data["name"],
                    color=label_data["color"],
                    description=label_data.get("description"),
                    url=label_data.get("url"),
                    is_default=label_data.get("isDefault", False),
                    created_at=(
                        datetime.fromisoformat(
                            label_data["createdAt"].replace("Z", "+00:00")
                        )
                        if label_data.get("createdAt")
                        else None
                    ),
                    updated_at=(
                        datetime.fromisoformat(
                            label_data["updatedAt"].replace("Z", "+00:00")
                        )
                        if label_data.get("updatedAt")
                        else None
                    ),
                )
            )
        return labels

    @classmethod
    def _parse_assignees(
        cls, assignees_data: Dict[str, Any]
    ) -> List[Union[User, "Organization"]]:
        """Parse assignees data from API response."""
        if not assignees_data or "nodes" not in assignees_data:
            return []

        assignees = []
        for assignee_data in assignees_data["nodes"]:
            assignees.append(cls._parse_owner_or_assignee(assignee_data))
        return assignees

    @classmethod
    def from_response(
        cls,
        data: Dict[str, Any],
        client: Optional[GraphQLClient] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> "Issue":
        """Create an Issue instance from API response data.

        Args:
            data (Dict[str, Any]): Raw issue data from API response
            client (Optional[GraphQLClient]): GraphQL client for API calls
            owner (Optional[str]): Owner of the repository
            repo (Optional[str]): Repository name

        Returns:
            Issue: New Issue instance
        """
        # Handle both issue-specific and project item responses
        if "content" in data:  # Project item response
            content = data["content"]
            return cls(
                id=content["id"],
                number=content["number"],
                title=content["title"],
                url=content["url"],
                state=content["state"],
                created_at=datetime.fromisoformat(
                    content["createdAt"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    content["updatedAt"].replace("Z", "+00:00")
                ),
                author_login=content.get("author", {}).get("login", ""),
                body=None,  # Not included in project responses
                field_values=data.get("fieldValues", {"nodes": []})["nodes"],
                client=client,
                owner=(
                    content["repository"]["owner"]["login"]
                    if content.get("repository", {}).get("owner")
                    else owner
                ),
                repo=(
                    content["repository"]["name"] if content.get("repository") else repo
                ),
                # New fields
                repository=cls._parse_repository(content.get("repository")),
                issue_owner=(
                    cls._parse_owner_or_assignee(content["repository"]["owner"])
                    if content.get("repository", {}).get("owner")
                    else None
                ),
                labels=cls._parse_labels(content.get("labels", {})),
                closed=content.get("closed", False),
                closed_at=(
                    datetime.fromisoformat(content["closedAt"].replace("Z", "+00:00"))
                    if content.get("closedAt")
                    else None
                ),
                assignees=cls._parse_assignees(content.get("assignees", {})),
            )
        else:  # Issue-specific response
            # For search results the data is in ["node"], directly in data,
            # or under repository.issue
            if "node" in data:
                issue_data = data["node"]
            elif "repository" in data and "issue" in data["repository"]:
                issue_data = data["repository"]["issue"]
            else:
                issue_data = data

            return cls(
                id=issue_data["id"],
                number=issue_data["number"],
                title=issue_data["title"],
                url=issue_data["url"],
                state=issue_data["state"],
                created_at=datetime.fromisoformat(
                    issue_data["createdAt"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    issue_data["updatedAt"].replace("Z", "+00:00")
                ),
                author_login=issue_data.get("author", {}).get("login", ""),
                body=issue_data.get("body"),
                field_values=[],  # Not included in issue responses
                client=client,
                owner=owner,
                repo=repo,
                # New fields (may not be available in all issue responses)
                repository=cls._parse_repository(issue_data.get("repository")),
                issue_owner=(
                    cls._parse_owner_or_assignee(issue_data["repository"]["owner"])
                    if issue_data.get("repository", {}).get("owner")
                    else None
                ),
                labels=cls._parse_labels(issue_data.get("labels", {})),
                closed=issue_data.get("closed", False),
                closed_at=(
                    datetime.fromisoformat(
                        issue_data["closedAt"].replace("Z", "+00:00")
                    )
                    if issue_data.get("closedAt")
                    else None
                ),
                assignees=cls._parse_assignees(issue_data.get("assignees", {})),
            )

    def get_comments(self, first: int = 20) -> List[Comment]:
        """Get comments on this issue.

        Args:
            first (int, optional): Number of comments to fetch per page. Defaults to 20.

        Returns:
            List[Comment]: Issue comments as Comment objects

        Raises:
            ValueError: If client, owner or repo are not set
            GraphQLError: On GraphQL operation failures
        """
        if not all([self.client, self.owner, self.repo]):
            raise ValueError("client, owner and repo must be set to fetch comments")

        query = load_query("get_issue_comments")
        variables = {
            "owner": self.owner,
            "repo": self.repo,
            "number": self.number,
            "first": first,
        }

        response = self.client.execute(query, variables)
        comments_data = response["repository"]["issue"]["comments"]
        comments = [Comment.from_response(node) for node in comments_data["nodes"]]
        return comments

    def get_timeline(self, first: int = 20) -> List[Event]:
        """Get timeline events on this issue.

        Args:
            first (int, optional): Number of events to fetch per page. Defaults to 20.

        Returns:
            List[Event]: Issue timeline events as Event objects

        Raises:
            ValueError: If client, owner or repo are not set
            GraphQLError: On GraphQL operation failures
        """
        if not all([self.client, self.owner, self.repo]):
            raise ValueError(
                "client, owner and repo must be set to fetch timeline events"
            )

        query = load_query("get_issue_timeline")
        variables = {
            "owner": self.owner,
            "repo": self.repo,
            "number": self.number,
            "first": first,
        }

        response = self.client.execute(query, variables)
        timeline_data = response["repository"]["issue"]["timelineItems"]
        nodes = [
            Event.create_from_response(node)
            for node in timeline_data["nodes"]
            if Event.create_from_response(node)
        ]
        return nodes

    def get_labels(self, first: int = 20, after: Optional[str] = None) -> List[Label]:
        """Get labels on this issue.

        Args:
            first (int, optional): Number of labels to fetch per page. Defaults to 20.
            after (Optional[str], optional): Cursor for pagination. Defaults to None.

        Returns:
            List[Label]: List of Label objects for the issue

        Raises:
            ValueError: If client, owner or repo are not set
            GraphQLError: On GraphQL operation failures
        """
        if not all([self.client, self.owner, self.repo]):
            raise ValueError("client, owner and repo must be set to fetch labels")

        query = load_query("get_issue_labels")
        variables = {
            "owner": self.owner,
            "repo": self.repo,
            "number": self.number,
            "first": first,
        }

        if after:
            variables["after"] = after

        response = self.client.execute(query, variables)
        labels_data = response["repository"]["issue"]["labels"]

        # Convert each node to a Label object and return the list directly
        return [
            Label(
                id=label["id"],
                name=label["name"],
                color=label["color"],
                description=label.get("description"),
                url=label.get("url"),
                created_at=Label.from_response(
                    {"repository": {"label": label}}
                ).created_at,
                updated_at=Label.from_response(
                    {"repository": {"label": label}}
                ).updated_at,
                is_default=label.get("isDefault", False),
                client=self.client,
            )
            for label in labels_data["nodes"]
        ]

    def get_fields(self, first: int = 20) -> List[Field]:
        """Get field values for this issue as Field objects.

        This method converts the raw field values from the API into Field instances.
        If field_values are already loaded, it will use those values.
        Otherwise, it will raise a ValueError as field values can only be
        loaded from a project.

        Args:
            first (int, optional): Number of fields to fetch per page. Defaults to 20.

        Returns:
            List[Field]: List of Field objects representing the issue's field values

        Raises:
            ValueError: If no field values are available
        """
        if not self.field_values:
            raise ValueError(
                "No field values available - field values can only be "
                "loaded from a project"
            )

        # Convert field values to Field instances
        fields = []
        for field_value in self.field_values:
            # Create a field data dictionary with the necessary fields
            field_data = {
                "id": field_value.get("field", {}).get("id", ""),
                "name": field_value.get("field", {}).get("name", ""),
                "type": field_value.get("__typename", ""),
                "dataType": field_value.get("field", {}).get("dataType")
                or field_value.get("__typename", "")
                .replace("ProjectV2ItemField", "")
                .replace("Value", "")
                .upper(),
            }

            # Fix for SingleSelect data type format
            if field_data["dataType"] == "SINGLESELECT":
                field_data["dataType"] = "SINGLE_SELECT"

            # Add field value based on the type
            if "text" in field_value:
                field_data["value"] = field_value["text"]
            elif "date" in field_value:
                field_data["value"] = field_value["date"]
            elif "name" in field_value:
                field_data["value"] = field_value["name"]
            # Handle user, repository, and milestone field types
            elif field_value.get("__typename") in [
                Field.USER,
                Field.REPOSITORY,
                Field.MILESTONE,
            ]:
                if field_value.get("__typename") == Field.USER:
                    # Handle users field (plural) - create User instances
                    # Users field is now a UserConnection with nodes structure
                    users_connection = field_value.get("users", {})
                    if isinstance(users_connection, dict):
                        users_data = users_connection.get("nodes", [])
                    else:
                        users_data = users_connection

                    if users_data:
                        field_data["value"] = [
                            User(
                                id="",  # Not available in the field response
                                login=user_data.get("login", ""),
                                name=None,
                                email=None,
                                bio=None,
                                company=None,
                                location=None,
                                website_url=None,
                                url="",  # Not available in the field response
                                avatar_url="",  # Not available in the field response
                            )
                            for user_data in users_data
                        ]
                    else:
                        field_data["value"] = []
                else:
                    # Handle repository and milestone fields (unchanged)
                    user_or_repo = field_value.get("repository") or field_value.get(
                        "milestone"
                    )
                    if user_or_repo:
                        field_data["value"] = user_or_repo.get(
                            "name"
                        ) or user_or_repo.get("title")

                # We no longer fetch options for SingleSelect fields

            fields.append(Field.from_response(field_data))

        return fields

    def get_subissues(self, first: int = 20) -> set["Issue"]:
        """Get sub-issues for this issue.

        Args:
            first (int, optional): Number of sub-issues to fetch per page.
                Defaults to 20.

        Returns:
            set[Issue]: Sub-issues as a set of Issue objects

        Raises:
            ValueError: If client, owner or repo are not set
            GraphQLError: On GraphQL operation failures
        """
        if not all([self.client, self.owner, self.repo]):
            raise ValueError("client, owner and repo must be set to fetch sub-issues")

        query = load_query("get_issue_subissues")
        variables = {
            "owner": self.owner,
            "repo": self.repo,
            "number": self.number,
            "first": first,
        }

        response = self.client.execute(query, variables)
        subissues_data = response["repository"]["issue"]["subIssues"]
        subissues = {
            Issue.from_response(node, self.client, self.owner, self.repo)
            for node in subissues_data["nodes"]
        }
        return subissues

    def get(
        self,
        *,
        client: GraphQLClient,
        repository: str,
        number: int,
        org: Optional[str] = None,
        username: Optional[str] = None,
    ) -> "Issue":
        """Get an issue's details and populate this instance.

        Args:
            client (GraphQLClient): GraphQL client for API calls
            repository (str): Repository name
            number (int): Issue number
            org (Optional[str]): Organization name (if issue is in an org's repo)
            username (Optional[str]): Username (if issue is in a user's repo)

        Returns:
            Issue: Self with populated properties

        Raises:
            ValueError: If neither org nor username is provided
            GraphQLError: On GraphQL operation failures
        """
        if not org and not username:
            raise ValueError("Either org or username must be provided")

        owner = org if org else username
        query = load_query("get_issue")
        variables = {"owner": owner, "repo": repository, "number": number}

        response = client.execute(query, variables)

        # Use from_response to create an issue instance with all properties
        issue = Issue.from_response(response, client, owner, repository)

        # Update this instance's attributes with the fetched data
        self.id = issue.id
        self.number = issue.number
        self.title = issue.title
        self.url = issue.url
        self.state = issue.state
        self.created_at = issue.created_at
        self.updated_at = issue.updated_at
        self.author_login = issue.author_login
        self.body = issue.body
        self.field_values = issue.field_values
        self.client = client
        self.owner = owner
        self.repo = repository

        return self
