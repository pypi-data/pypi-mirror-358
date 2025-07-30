"""Custom exceptions for the GitHub GraphQL client."""


class GraphQLError(Exception):
    """Base exception for GitHub GraphQL API errors.
    
    Attributes:
        errors (list): List of GraphQL error dictionaries from the API response
        message (str): General error message
    """

    def __init__(self, message: str, errors=None):
        """Initialize the exception.

        Args:
            message (str): Error message
            errors (list, optional): List of GraphQL errors
        """
        super().__init__(message)
        self.errors = errors or []
    
    def __str__(self):
        """Return a string representation of the error.
        
        Returns:
            str: Formatted error message including API errors if available
        """
        if not self.errors:
            return super().__str__()
        
        error_messages = [f"- {error.get('message', 'Unknown error')}" for error in self.errors]
        return f"{super().__str__()}: \n" + "\n".join(error_messages)


class AuthenticationError(GraphQLError):
    """Raised when there are authentication issues."""

    pass


class RateLimitError(GraphQLError):
    """Raised when GitHub's rate limit is exceeded."""

    pass
