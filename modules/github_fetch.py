"""
github_fetch.py — All GitHub REST API calls.

This is the ONLY file that talks to the GitHub API.
Every requests.get() call uses timeout=10.

fetch_repo_info(owner, repo) → dict
fetch_tree(owner, repo, branch) → list[dict]
fetch_readme(owner, repo) → str
fetch_issues(owner, repo) → list[dict]   (pull requests filtered out)
fetch_dependency_file(owner, repo) → list[str] | None

Wired in: Step 2
"""


def fetch_repo_info(owner: str, repo: str) -> dict:
    """Return basic repo metadata from GET /repos/{owner}/{repo}. Step 2."""
    raise NotImplementedError("github_fetch.fetch_repo_info — implemented in Step 2")


def fetch_tree(owner: str, repo: str, branch: str) -> list[dict]:
    """Return the recursive file tree. Each item has 'path', 'type', 'size'. Step 2."""
    raise NotImplementedError("github_fetch.fetch_tree — implemented in Step 2")


def fetch_readme(owner: str, repo: str) -> str:
    """Return the decoded README text. Empty string if not found. Step 2."""
    raise NotImplementedError("github_fetch.fetch_readme — implemented in Step 2")


def fetch_issues(owner: str, repo: str) -> list[dict]:
    """
    Return open issues (pull requests filtered out).
    Each item has 'number', 'title', 'html_url', 'body', 'labels'. Step 2.
    """
    raise NotImplementedError("github_fetch.fetch_issues — implemented in Step 2")


def fetch_dependency_file(owner: str, repo: str) -> list[str] | None:
    """
    Try requirements.txt then package.json.
    Return a list of dependency name strings, or None if neither exists. Step 2.
    """
    raise NotImplementedError(
        "github_fetch.fetch_dependency_file — implemented in Step 2"
    )
