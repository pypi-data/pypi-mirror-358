# GitHub GraphQL API Client

A Python module for working with GitHub's GraphQL API, with a focus on ProjectsV2 functionality.

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

1. First, [install Poetry](https://python-poetry.org/docs/#installation) if you haven't already.

1. Install the package:

```bash
# Install for use
poetry install

# Install with development dependencies
poetry install --with dev
```

3. Activate the Poetry virtual environment:

```bash
poetry shell
```

## Usage

Basic usage example:

```python
from gh_project_v2 import ProjectsV2Client

# Initialize the client (simplified approach)
projects = ProjectsV2Client("your-github-token")

# Get project details
project = projects.get_project(
    project_number=1,
    owner="octocat"
)

# List project fields
fields = projects.list_project_fields("project-node-id")
```

### Advanced Usage

For more control over the GraphQL client configuration, you can still use the traditional approach:

```python
from gh_project_v2 import GraphQLClient, ProjectsV2Client

# Initialize with custom GraphQL client
client = GraphQLClient("your-github-token", api_url="https://custom-github.com/graphql")
projects = ProjectsV2Client(client)
```

### Error Handling

When using the GraphQL client, you can catch exceptions to handle errors:

```python
from gh_project_v2 import GraphQLClient
from gh_project_v2.exceptions import GraphQLError

client = GraphQLClient("your-github-token")

try:
    result = client.execute("query { test }")
except GraphQLError as e:
    # Access the list of GraphQL errors
    print(f"GraphQL errors: {e.errors}")
    
    # The string representation of the exception now includes all error messages
    print(f"Error details: {e}")
```

The `GraphQLError` exception includes:
- A `message` attribute with the general error message
- An `errors` attribute containing the list of specific errors from the API
- A string representation that includes all error messages for easy debugging`

## Logging

The library provides a simple logging helper function that can be used throughout your application to log messages to a file. Logging is controlled by the `LOG_FILE` environment variable, making it easy to enable or disable as needed.

### Basic Usage

```python
import os
from gh_project_v2 import log_message

# Set the log file location
os.environ['LOG_FILE'] = '/path/to/logfile.log'

# Log messages with automatic timestamps
log_message("Application started")
log_message("Processing user request")
log_message("Request completed successfully")

# Disable logging by removing the environment variable
del os.environ['LOG_FILE']
log_message("This won't be logged")
```

### Features

- **Environment-controlled logging**: Only logs when `LOG_FILE` environment variable is set
- **Standardized format**: Uses `[%Y-%m-%d %H:%M:%S] <message>` format
- **Automatic directory creation**: Creates parent directories if they don't exist
- **Error handling**: Gracefully handles file permission and I/O errors without disrupting the main application
- **Unicode support**: Handles unicode characters and multiline messages correctly
- **Append mode**: Appends to existing log files rather than overwriting

### Example Output

```
[2025-01-15 10:30:45] Application started
[2025-01-15 10:30:45] Processing user request
[2025-01-15 10:30:46] Request completed successfully
```

### Usage in Your Code

You can use the logging function anywhere in your application:

```python
from gh_project_v2 import ProjectsV2Client, log_message
import os

# Enable logging
os.environ['LOG_FILE'] = '/var/log/gh-project.log'

# Initialize client with logging
log_message("Initializing GitHub Projects client")
projects = ProjectsV2Client("your-github-token")

try:
    # Get project with logging
    log_message("Fetching project details")
    project = projects.get_project(project_number=1, owner="octocat")
    log_message(f"Successfully retrieved project: {project.title}")
    
    # Process items with logging  
    items = project.get_items(first=10)
    log_message(f"Found {len(items['nodes'])} items in project")
    
except Exception as e:
    log_message(f"Error occurred: {str(e)}")
    raise
```

## Issue vs DraftIssue

The library supports both regular Issues and DraftIssues from GitHub Projects V2. Here are the key differences:

### Issue
Regular GitHub issues with full metadata:
- `number`: Issue number (e.g., #123)
- `url`: Direct URL to the issue
- `state`: Issue state (OPEN, CLOSED)
- `author`: Issue author information
- Full access to comments, labels, timeline events, and sub-issues

#### Sub-Issues
Issues can have sub-issues that can be fetched using the `get_subissues()` method:

```python
# Get an issue and its sub-issues
issue = projects.get_issue("owner", "repo", 123)
subissues = issue.get_subissues()

print(f"Issue #{issue.number} has {len(subissues)} sub-issues:")
for subissue in subissues:
    print(f"  - Sub-issue #{subissue.number}: {subissue.title} ({subissue.state})")
```

The `get_subissues()` method returns a set of Issue objects, ensuring no duplicates.

### DraftIssue
Draft issues are project-specific items that don't exist as repository issues:
- `number`: Always 0 (DraftIssue doesn't have issue numbers)
- `url`: Always empty string (no direct URL)
- `state`: Always empty string (no state concept)
- `creator`: Draft issue creator (equivalent to author)
- Limited metadata compared to regular issues

```python
# Example: Working with both types
items = project.get_items()

for item in items:
    if isinstance(item, DraftIssue):
        print(f"Draft Issue: {item.title} (created by {item.author_login})")
        # item.number will be 0, item.url will be ""
    elif isinstance(item, Issue):
        print(f"Issue #{item.number}: {item.title} ({item.state})")
        # item.number will be the actual issue number
```

## Features

- Base GraphQL client with authentication and error handling
- ProjectsV2-specific operations:
  - Get project details (supports both user and organization projects)
  - List project fields with Field and Option objects
  - Get project repositories, teams, and workflows
- Support for GitHub objects:
  - Teams with properties like name, slug, description, privacy, member count, etc.
  - Workflows with properties like name, path, state, URL, file contents, etc.

## Examples

### Access Field and Option objects

Get fields from a project and access their properties:

```python
from gh_project_v2 import GraphQLClient, ProjectsV2Client
from gh_project_v2.models import Field, Option

# Initialize client
client = GraphQLClient("your-github-token")
projects = ProjectsV2Client(client)

# Get a project
project = projects.get_project(
    project_number=1,
    owner="octocat"
)

# Get fields as Field objects
fields = projects.list_project_fields(project.id)

# Access field properties
for field in fields:
    print(f"Field: {field.name}, Type: {field.data_type}")
    
    # For single select fields, access the options
    if field.data_type == "SINGLE_SELECT" and field.options:
        print("Options:")
        for option in field.options:
            print(f"  - {option.name} (ID: {option.id})")
```

### Supported Field Types

The library supports various field types from GitHub Projects:

- `ProjectV2ItemFieldTextValue`: For text fields
- `ProjectV2ItemFieldDateValue`: For date fields
- `ProjectV2ItemFieldSingleSelectValue`: For single select fields
- `ProjectV2ItemFieldUserValue`: For user fields
- `ProjectV2ItemFieldRepositoryValue`: For repository fields
- `ProjectV2ItemFieldMilestoneValue`: For milestone fields
- `ProjectV2ItemFieldNumberValue`: For number fields
- Generic `ProjectV2Field`: For other field types

#### Field Type Constants

The `Field` class provides constants for easy type checking:

| Constant | Value |
|----------|-------|
| `Field.TEXT` | `"ProjectV2ItemFieldTextValue"` |
| `Field.DATE` | `"ProjectV2ItemFieldDateValue"` |
| `Field.SINGLE_SELECT` | `"ProjectV2ItemFieldSingleSelectValue"` |
| `Field.USER` | `"ProjectV2ItemFieldUserValue"` |
| `Field.REPOSITORY` | `"ProjectV2ItemFieldRepositoryValue"` |
| `Field.MILESTONE` | `"ProjectV2ItemFieldMilestoneValue"` |
| `Field.NUMBER` | `"ProjectV2ItemFieldNumberValue"` |

Example accessing different field types:

```python
# Get issues with field values
items = project.get_issues(first=10)

# Print field values
for item in items:
    fields = item.get_fields()
    for field in fields:
        print(f"Field: {field.name}, Type: {field.data_type}, Value: {field.value}")

        # Example handling different field types
        if field.type == Field.USER:
            print(f"  User field: {field.value}")
        elif field.type == Field.REPOSITORY:
            print(f"  Repository field: {field.value}")
        elif field.type == Field.MILESTONE:
            print(f"  Milestone field: {field.value}")
```

# Find a specific field by name

```python
status_field = project.find_field_by_name("Status")
if status_field:
    print(f"Found field: {status_field.name}, Type: {status_field.data_type}")
```

### Get Project

Access a project by its number and owner:

```python
from gh_project_v2 import GraphQLClient, ProjectsV2Client
from gh_project_v2.models import Field, Option
```

# Initialize client

```python
client = GraphQLClient("your-github-token")
projects = ProjectsV2Client(client)
```

# Get a project

```python
project = projects.get_project(
    project_number=1,
    owner="octocat"
)
```

# Get fields as Field objects

`fields = projects.list_project_fields(project.id)`

# Access field properties

```python
for field in fields:
    print(f"Field: {field.name}, Type: {field.data_type}")
    
    # For single select fields, access the options
    if field.data_type == "SINGLE_SELECT" and field.options:
        print("Options:")
        for option in field.options:
            print(f"  - {option.name} (ID: {option.id})")
```

# Find a specific field by name

```python
status_field = project.find_field_by_name("Status")
if status_field:
    print(f"Found field: {status_field.name}, Type: {status_field.data_type}")
```

### Get Models Directly

You can get issues, labels, repositories, organizations, pull requests, users, views, teams, workflows, projects, options, milestones, fields, and comments directly using their respective models:

```python
from gh_project_v2 import GraphQLClient
from gh_project_v2.models import Issue, Label, Repository, Organization, PullRequest, User, View
from gh_project_v2.models import Team, Workflow, Project, Option, Milestone, Field, Comment
from datetime import datetime

# Initialize client
client = GraphQLClient("your-github-token")

# Get an issue
issue = Issue()  # Create empty issue
issue.get(
    client=client,
    repository="example-repo",
    number=42,
    username="octocat"  # or use org="github" for organization repos
)
print(f"Issue #{issue.number}: {issue.title}")

# Get a label by name
label = Label()  # Create empty label
label.get(
    client=client,
    repository="example-repo",
    name="bug",
    owner="octocat"
)
print(f"Label: {label.name}, Color: #{label.color}")

# Get a label by ID
label_by_id = Label()  # Create empty label
label_by_id.get(
    client=client,
    repository="example-repo",
    id="L_abc123"
)
print(f"Label: {label_by_id.name}, Color: #{label_by_id.color}")

# Get a repository
repo = Repository()  # Create empty repository
repo.get(
    client=client,
    name="example-repo",
    username="octocat"  # or use org="github" for organization repos
)
print(f"Repository: {repo.name_with_owner}, Private: {repo.is_private}")

# Get an organization by name
org = Organization(id="", login="")
org.get(
    client=client,
    name="github"
)
print(f"Organization: {org.name}, Login: {org.login}")

# Get an organization by ID
org_by_id = Organization(id="", login="")
org_by_id.get(
    client=client,
    id="O_abc123"
)
print(f"Organization: {org_by_id.name}, Login: {org_by_id.login}")

# Get a pull request
pr = PullRequest(id="", number=0, title="", url="", state="", field_values=[], author_login="")
pr.get(
    client=client,
    repository="example-repo",
    number=42,
    username="octocat"  # or use org="github" for organization repos
)
print(f"PR #{pr.number}: {pr.title}, State: {pr.state}")

# Get a user by username
user = User(id="", login="", name=None, email=None, bio=None, company=None, location=None, 
           website_url=None, url="", avatar_url="")
user.get(
    client=client,
    username="octocat"
)
print(f"User: {user.login}, Name: {user.name}")

# Get a user by ID
user_by_id = User(id="", login="", name=None, email=None, bio=None, company=None, location=None, 
                 website_url=None, url="", avatar_url="")
user_by_id.get(
    client=client,
    id="U_abc123"
)
print(f"User: {user_by_id.login}, Name: {user_by_id.name}")

# Get a view by ID
view = View(id="", name="", number=0, layout="", fields=[])
view.get(
    client=client,
    id="PVV_abc123"
)
print(f"View: {view.name}, Layout: {view.layout}")

# Get a view by name (requires project_id)
view_by_name = View(id="", name="", number=0, layout="", fields=[])
view_by_name.get(
    client=client,
    name="Kanban",
    project_id="PVT_abc123"
)
print(f"View: {view_by_name.name}, Layout: {view_by_name.layout}")

# Get a team by org name and slug
team = Team(id="", name="", slug="")
team.get(
    client=client,
    org="example-org",
    slug="engineering"
)
print(f"Team: {team.name}, Slug: {team.slug}")

# Get a workflow by ID
workflow = Workflow(id="", name="", path="", state="")
workflow.get(
    client=client,
    id="W_abc123"
)
print(f"Workflow: {workflow.name}, State: {workflow.state}")

# Get a project by owner and number
project = Project(id="", title="", short_description=None, public=False, closed=False, url="", number=0, client=client)
project.get(
    client=client,
    owner="octocat",
    number=1
)
print(f"Project: {project.title}, Number: {project.number}")

# Get an option by ID
option = Option(id="", name="")
option.get(
    client=client,
    id="PVSO_abc123"
)
print(f"Option: {option.name}")

# Get a milestone by repository, owner, and number
milestone = Milestone(id="", number=0, title="", url="", state="", description=None)
milestone.get(
    client=client,
    repository="example-repo",
    number=1,
    owner="octocat"
)
print(f"Milestone: {milestone.title}, State: {milestone.state}")

# Get a field by ID
field = Field(id="", name="", data_type="", options=[])
field.get(
    client=client,
    id="PVF_abc123"
)
print(f"Field: {field.name}, Data Type: {field.data_type}")

# Get a comment by ID
comment = Comment(id="", body="", url="", created_at=dt, updated_at=dt, author_login="")
comment.get(
    client=client,
    id="IC_abc123"
)
print(f"Comment by {comment.author_login}: {comment.body}")
```

### Helper Methods for Related Data

You can use helper methods to fetch related data from GitHub objects with pagination support:

```python
from gh_project_v2 import GraphQLClient
from gh_project_v2.models import Organization, Repository

# Initialize client
client = GraphQLClient("your-github-token")

# Get repositories in an organization
org = Organization(id="", login="")
org.get(client=client, name="github")

# Get first 10 repositories in the organization
repos = org.get_repos(first=10)
print(f"Found {len(repos['nodes'])} repositories")
for repo in repos['nodes']:
    print(f"Repository: {repo.name}, URL: {repo.url}")

# Pagination example - get next page of repositories
if repos["pageInfo"]["hasNextPage"]:
    more_repos = org.get_repos(first=10, after=repos["pageInfo"]["endCursor"])
    print(f"Found {len(more_repos['nodes'])} more repositories")

# Get members (users) in an organization
users = org.get_users(first=5)
print(f"\nFound {len(users['nodes'])} users")
for user in users['nodes']:
    print(f"User: {user.login}, Name: {user.name}")

# Get repository by name
repo = Repository()
repo.get(client=client, name="actions", org="github")

# Get labels in a repository
labels = repo.get_labels(first=15)
print(f"\nFound {len(labels['nodes'])} labels")
for label in labels['nodes']:
    print(f"Label: {label.name}, Color: #{label.color}")

# Get pull requests in a repository
prs = repo.get_pull_requests(first=5)
print(f"\nFound {len(prs['nodes'])} pull requests")
for pr in prs['nodes']:
    print(f"PR #{pr.number}: {pr.title}, State: {pr.state}")

# Pagination for pull requests
if prs["pageInfo"]["hasNextPage"]:
    more_prs = repo.get_pull_requests(first=5, after=prs["pageInfo"]["endCursor"])
    print(f"Found {len(more_prs['nodes'])} more pull requests")

# Get issues in a repository
issues = repo.get_issues(first=5)
print(f"\nFound {len(issues['nodes'])} issues")
for issue in issues['nodes']:
    print(f"Issue #{issue.number}: {issue.title}, State: {issue.state}")

# Get discussions in a repository
discussions = repo.get_discussions(first=5)
print(f"\nFound {len(discussions['nodes'])} discussions")
for discussion in discussions['nodes']:
    print(f"Discussion #{discussion['number']}: {discussion['title']}")

# Get milestones in a repository
milestones = repo.get_milestones(first=5)
print(f"\nFound {len(milestones['nodes'])} milestones")
for milestone in milestones['nodes']:
    print(f"Milestone: {milestone.title}, State: {milestone.state}")

# Get releases in a repository
releases = repo.get_releases(first=5)
print(f"\nFound {len(releases['nodes'])} releases")
for release in releases['nodes']:
    print(f"Release: {release['name']}, Tag: {release['tagName']}")

# Get project by number
from gh_project_v2.models import Project
from gh_project_v2.projects_v2 import ProjectsV2Client

projects_client = ProjectsV2Client(client)
project = projects_client.get_project(project_number=123, owner="octocat")

# Get repositories in a project
repositories = project.get_repositories(first=10)
print(f"\nFound {len(repositories)} repositories in project")
for repo in repositories:
    print(f"Repository: {repo.name}, URL: {repo.url}")

# Get teams in a project
teams = project.get_teams(first=5)
print(f"\nFound {len(teams)} teams in project")
for team in teams:
    print(f"Team: {team.name}, Members: {team.members_count}")

# Get workflows in a project
workflows = project.get_workflows(first=5)
print(f"\nFound {len(workflows)} workflows in project")
for workflow in workflows:
    print(f"Workflow: {workflow.name}, Path: {workflow.path}, State: {workflow.state}")
```

### Enhanced Issue and PullRequest Fields

When fetching issues and pull requests from projects using `project.get_items()`, the following additional fields are now available:

#### Issue Fields
```python
# Get project items
items = project.get_items(first=10)

for item in items:
    if isinstance(item, Issue):
        print(f"Issue #{item.number}: {item.title}")
        print(f"State: {item.state}, Closed: {item.closed}")
        
        # Repository information
        if item.repository:
            print(f"Repository: {item.repository.name_with_owner}")
            print(f"Private: {item.repository.is_private}")
            print(f"Description: {item.repository.description}")
        
        # Repository owner (can be User or Organization)
        if item.issue_owner:
            print(f"Owner: {item.issue_owner.login} ({type(item.issue_owner).__name__})")
        
        # Labels
        if item.labels:
            print(f"Labels: {', '.join(label.name for label in item.labels)}")
        
        # Assignees (can be Users or Organizations)
        if item.assignees:
            assignee_names = [assignee.login for assignee in item.assignees]
            print(f"Assignees: {', '.join(assignee_names)}")
        
        # Closed information
        if item.closed and item.closed_at:
            print(f"Closed at: {item.closed_at}")
```

#### Available Fields
- **`repository`**: `Repository` object with full repository details
- **`issue_owner`**: Repository owner as `User` or `Organization` object
- **`labels`**: List of `Label` objects attached to the issue
- **`closed`**: Boolean indicating if the issue/PR is closed
- **`closed_at`**: DateTime when the issue/PR was closed (if applicable)
- **`assignees`**: List of `User` or `Organization` objects assigned to the issue

#### PullRequest Fields
PullRequest objects have the same enhanced fields as Issues:
```python
for item in items:
    if isinstance(item, PullRequest):
        print(f"PR #{item.number}: {item.title}")
        
        # Same fields available as Issues
        if item.pr_owner:  # Note: field name is pr_owner for PullRequest
            print(f"Owner: {item.pr_owner.login}")
```

### Get Project Items

Retrieve issues, draft issues, and pull requests from a project with their field values:

**Note on DraftIssue**: DraftIssue objects in GitHub Projects have a different schema than regular Issues. DraftIssue doesn't have `number`, `url`, or `state` fields in the GitHub GraphQL API. When working with DraftIssue objects through this library, these fields are set to default values (`number=0`, `url=""`, `state=""`) for compatibility with the Issue base class.

```python
# Get items with custom field values (default 20 per page)
items = project.get_items(first=10, fields_first=50)

# Example response:
# {
#   "nodes": [
#     {
#       "id": "PVTI_...",
#       "fieldValues": {
#         "nodes": [
#           {
#             "text": "High Priority",
#             "field": {"name": "Priority"}
#           },
#           {
#             "date": "2024-05-01",
#             "field": {"name": "Due Date"}
#           }
#         ]
#       },
#       "content": {
#         "id": "I_...",
#         "number": 123,
#         "title": "Add new feature",
#         "url": "https://github.com/org/repo/issues/123",
#         "state": "OPEN",
#         "createdAt": "2024-01-01T00:00:00Z",
#         "updatedAt": "2024-01-02T00:00:00Z"
#       }
#     }
#   ]
# }
```

#### Working with Issue Field Values

You can convert raw field values from an issue to structured `Field` objects using the `get_fields` method:

```python
# Get an issue with field values from a project
issues = project.get_issues(first=20)
issue = issues["nodes"][0]  # Get first issue

# Convert to Field objects for easier access
fields = issue.get_fields()

# Now you can work with structured Field objects
for field in fields:
    print(f"Field: {field.name}, Type: {field.data_type}, Value: {field.value}")

# Find a specific field by name
priority_field = next((f for f in fields if f.name == "Priority"), None)
if priority_field and priority_field.value == "High":
    print(f"High priority issue: {issue.title}")

# Access fields by data type
date_fields = [f for f in fields if f.data_type == "DATE"]
for date_field in date_fields:
    print(f"{date_field.name}: {date_field.value}")
```

The `get_fields` method handles different field types automatically (text, date, select) and will raise a `ValueError` if no field values are available in the issue.

#### Getting Issue Labels

You can retrieve the labels for an issue with the `get_labels` method:

```python
# Get an issue
issue = Issue()
issue.get(
    client=client, 
    repository="example-repo", 
    number=42,
    username="octocat"  # or use org="github" for organization repos
)

# Get labels for the issue
labels = issue.get_labels(first=10)  # Get first 10 labels
print(f"Issue #{issue.number} has {len(labels)} labels:")

for label in labels:
    print(f"- {label.name} (#{label.color}): {label.description or 'No description'}")

# Check for a specific label
bug_label = next((l for l in labels if l.name == "bug"), None)
if bug_label:
    print("This issue is marked as a bug!")
```

### Get Project Views

Fetch configured views and their fields:

```python
# Get project views (defaults to 20 views per page)
views = project.get_views()

# Get specific number of views per page
views = project.get_views(first=10)

# Example response:
# {
#   "nodes": [
#     {
#       "id": "PVV_...",
#       "name": "Board View", 
#       "number": 1,
#       "layout": "BOARD_LAYOUT",
#       "fields": {
#         "nodes": [
#           {
#             "id": "PVF_...",
#             "name": "Status"
#           },
#           {
#             "id": "PVF_...",
#             "name": "Priority"
#           }
#         ]
#       }
#     }
#   ],
#   "pageInfo": {
#     "hasNextPage": false,
#     "endCursor": null
#   }
# }
```

### Search

Search for issues, pull requests and repositories:

```python
from gh_project_v2 import GraphQLClient, ProjectsV2Client, SearchType

# Initialize client
client = GraphQLClient("your-github-token")
projects = ProjectsV2Client(client)

# Search for issues
results = projects.search("is:open is:issue label:bug", SearchType.ISSUE)

# Search for repositories
repos = projects.search("stars:>1000 language:python", SearchType.REPOSITORY)

# Example response:
# {
#   "nodes": [
#     {
#       "id": "I_...",
#       "number": 123,
#       "title": "Fix memory leak",
#       "url": "https://github.com/owner/repo/issues/123",
#       "state": "OPEN",
#       "createdAt": "2024-01-01T00:00:00Z",
#       "updatedAt": "2024-01-02T00:00:00Z",
#       "author": {
#         "login": "username"
#       },
#       "repository": {
#         "nameWithOwner": "owner/repo"
#       }
#     }
#   ],
#   "pageInfo": {
#     "hasNextPage": true,
#     "endCursor": "Y3Vyc29yOjYw"
#   }
# }
```

### Independent Data Fetching

In addition to ProjectsV2 operations, you can fetch GitHub data independently:

```python
from gh_project_v2 import GraphQLClient, ProjectsV2Client

# Initialize client
client = GraphQLClient("your-github-token")
projects = ProjectsV2Client(client)

# Get user profile
user = projects.get_user("octocat")
print(f"User: {user.login}, Name: {user.name}")

# Get user followers
followers = user.get_followers(first=5)
print(f"Found {len(followers['nodes'])} followers")
for follower in followers['nodes']:
    print(f"Follower: {follower.login}, Name: {follower.name}")

# Get users that the user follows
following = user.get_following(first=5)
print(f"Found {len(following['nodes'])} users that {user.login} follows")
for followed in following['nodes']:
    print(f"Following: {followed.login}, Name: {followed.name}")

# Get issues assigned to a user
user_issues = user.get_issues(first=5)
print(f"Found {len(user_issues['nodes'])} issues assigned to {user.login}")
for issue in user_issues['nodes']:
    print(f"Issue #{issue.number}: {issue.title} ({issue.state})")

# Get issue with comments
issue = projects.get_issue("owner", "repo", 123)
print(f"Issue #{issue.number}: {issue.title}")

# Get issue comments
comments = issue.get_comments()
for comment in comments:
    print(f"Comment by {comment.author}: {comment.body}")

# Get issue sub-issues
subissues = issue.get_subissues()
print(f"Found {len(subissues)} sub-issues for issue #{issue.number}")
for subissue in subissues:
    print(f"Sub-issue #{subissue.number}: {subissue.title} ({subissue.state})")

# Get a milestone from a repository
milestone = Milestone(id="", number=0, title="", url="", state="")
milestone.get(client=client, owner="octocat", repo="hello-world", number=1)
print(f"Milestone: {milestone.title}, State: {milestone.state}")

# Get issues for a milestone
milestone_issues = milestone.get_issues(first=5)
print(f"Found {len(milestone_issues['nodes'])} issues in milestone {milestone.title}")
for issue in milestone_issues['nodes']:
    print(f"Issue #{issue.number}: {issue.title} ({issue.state})")

# Get pull requests for a milestone
milestone_prs = milestone.get_pull_requests(first=5)
print(f"Found {len(milestone_prs['nodes'])} pull requests in milestone {milestone.title}")
for pr in milestone_prs['nodes']:
    print(f"PR #{pr.number}: {pr.title} ({pr.state})")

# Get repository for a milestone
milestone_repo = milestone.get_repo()
print(f"Milestone '{milestone.title}' belongs to repository: {milestone_repo.name_with_owner}")

# Get a project and its views
project = projects.get_project(
    project_number=1,
    owner="octocat"
)
views = project.get_views()
for view in views:
    print(f"View: {view.name}, Layout: {view.layout}")
```

## Development

### Testing

Run tests inside Poetry environment with:

```bash
poetry run pytest tests/
```

### Code Style

Format code with:

```bash
poetry run black github_gql tests examples
```

Lint code with:

```bash
poetry run flake8 github_gql tests examples
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Supported Events

The following event types are supported for issue timelines:

- AddedToProjectEvent
- AssignedEvent
- ClosedEvent
- CommentDeletedEvent
- CrossReferencedEvent
- DemilestonedEvent
- IssueCommentEvent
- IssueTypeAddedEvent
- IssueTypeChangedEvent
- IssueTypeRemovedEvent
- LabeledEvent
- LockedEvent
- MarkedAsDuplicateEvent
- MentionedEvent
- MergedEvent
- MilestonedEvent
- MovedColumnsInProjectEvent
- ParentIssueAddedEvent
- ParentIssueRemovedEvent
- PinnedEvent
- ReferencedEvent
- RenamedTitleEvent
- ReopenedEvent
- SubIssueAddedEvent
- SubIssueRemovedEvent
- SubscribedEvent
- TransferredEvent
- UnassignedEvent
- UnlabeledEvent
- UnsubscribedEvent
