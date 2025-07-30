"""GitHub API clients for different types of data."""

from typing import Dict, Any
from enum import Enum
from .client import GraphQLClient


class SearchType(str, Enum):
    """Supported GitHub search types."""
    ISSUE = "ISSUE"
    REPOSITORY = "REPOSITORY"


def _paginate_query(
    client: GraphQLClient,
    query: str,
    variables: Dict[str, Any],
    data_path: str,
    nested_path: str = None,
) -> Dict[str, Any]:
    """Helper method to handle pagination in GraphQL queries.

    Args:
        client (GraphQLClient): GraphQL client
        query (str): GraphQL query string
        variables (Dict[str, Any]): Query variables
        data_path (str): Path to nodes array in response (e.g. "node.fields" or "node.items")
        nested_path: Path to nested nodes for nested pagination (e.g. "fieldValues")

    Returns:
        Dict[str, Any]: Merged results from all pages
    """
    all_nodes = []
    has_next_page = True
    after = None

    while has_next_page:
        curr_vars = {**variables}
        if after:
            curr_vars["after"] = after

        result = client.execute(query, curr_vars)

        # Navigate to the nodes data using data_path
        curr_data = result
        for key in data_path.split("."):
            curr_data = curr_data.get(key, {})

        nodes = curr_data.get("nodes", [])

        # Handle nested pagination if requested
        if nested_path:
            for node in nodes:
                curr_nested_data = node.get(nested_path, {})
                has_next_nested = curr_nested_data.get("pageInfo", {}).get(
                    "hasNextPage", False
                )
                nested_cursor = curr_nested_data.get("pageInfo", {}).get(
                    "endCursor"
                )
                nested_nodes = curr_nested_data.get("nodes", [])

                all_nested_nodes = nested_nodes.copy()

                # Paginate through nested nodes
                while has_next_nested:
                    curr_vars = {**variables}  # Start fresh
                    curr_vars.update({"fieldsAfter": nested_cursor})
                    nested_result = client.execute(query, curr_vars)

                    # Navigate to same location
                    curr_nested_result = nested_result
                    for key in data_path.split("."):
                        curr_nested_result = curr_nested_result.get(key, {})

                    # Get first node's fieldValues since we're paginating its fields
                    curr_nested_data = curr_nested_result["nodes"][0].get(
                        nested_path, {}
                    )

                    nested_nodes = curr_nested_data.get("nodes", [])
                    all_nested_nodes.extend(nested_nodes)

                    has_next_nested = curr_nested_data.get("pageInfo", {}).get(
                        "hasNextPage", False
                    )
                    nested_cursor = curr_nested_data.get("pageInfo", {}).get(
                        "endCursor"
                    )

                # Update node with merged nested nodes
                node[nested_path]["nodes"] = all_nested_nodes

        all_nodes.extend(nodes)

        page_info = curr_data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        after = page_info.get("endCursor")

    # Reconstruct response with all nodes
    response = result  # Start with last response
    curr_data = response
    *parent_keys, last_key = data_path.split(".")

    # Navigate to the parent object to update
    for key in parent_keys:
        curr_data = curr_data[key]

    curr_data[last_key]["nodes"] = all_nodes
    return response