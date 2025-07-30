"""GitHub GraphQL API client library focused on ProjectsV2 functionality."""

from .client import GraphQLClient
from .projects_v2 import ProjectsV2Client, SearchType
from .exceptions import GraphQLError
from .models.issue import Issue
from .models.view import View  
from .models.user import User
from .models.comment import Comment
from .models.field import Field
from .utils import log_message

__version__ = "0.1.0"
__all__ = [
    "GraphQLClient", "ProjectsV2Client", "GraphQLError",
    "SearchType", 
    "Issue", "View", "User", "Comment", "Field",
    "log_message"
]
