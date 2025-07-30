"""Base GraphQL client implementation for GitHub's API."""

import requests
from typing import Dict, Any, Optional

from .exceptions import GraphQLError, AuthenticationError, RateLimitError


class GraphQLClient:
    """Base client for making GraphQL requests to GitHub's API."""

    def __init__(self, token: str, api_url: str = "https://api.github.com/graphql"):
        """Initialize the GraphQL client.

        Args:
            token (str): GitHub Personal Access Token
            api_url (str, optional): GitHub GraphQL API endpoint
        """
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v4+json",
            }
        )

    def execute(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query or mutation.

        Args:
            query (str): GraphQL query or mutation string
            variables (dict, optional): Variables for the GraphQL operation

        Returns:
            dict: Response data from the API

        Raises:
            GraphQLError: On general GraphQL errors
            AuthenticationError: On authentication failures
            RateLimitError: When rate limit is exceeded
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = self.session.post(self.api_url, json=payload)

        if response.status_code == 401:
            raise AuthenticationError("Invalid authentication credentials")
        elif response.status_code == 403:
            raise RateLimitError("API rate limit exceeded")

        data = response.json()
        if "errors" in data:
            raise GraphQLError("GraphQL operation failed", data["errors"])

        return data.get("data", {})
