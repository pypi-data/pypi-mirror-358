"""GraphQL query templates package."""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Create Jinja2 environment pointing to queries directory
env = Environment(
    loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
    autoescape=select_autoescape(),
)


def load_query(template_name: str) -> str:
    """Load and return a GraphQL query template.

    Args:
        template_name (str): Name of the file without .graphql extension

    Returns:
        str: The loaded query template
    """
    return env.get_template(f"{template_name}.graphql").render()
