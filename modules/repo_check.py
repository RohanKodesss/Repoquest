"""
repo_check.py — URL parsing and playability constants.

parse_repo_url(url) → (owner, repo) | None
playability_check(tree_items, issues, dependency_names) → (ok, warnings)

Wired in: Step 2
"""

# Playability thresholds (API Spec Rev 4, section 2.2)
MIN_REPO_FILES = 5
MIN_REPO_FOLDERS = 2


def parse_repo_url(url: str) -> tuple[str, str] | None:
    """
    Return (owner, repo) for a valid github.com/owner/repo URL, else None.
    Strips https://, www., .git, trailing slash, /tree/branch, query strings,
    and fragments.
    Implemented in Step 2.
    """
    raise NotImplementedError("repo_check.parse_repo_url — implemented in Step 2")


def playability_check(
    tree_items: list[dict],
    issues: list[dict],
    dependency_names: list[str],
) -> tuple[bool, list[str]]:
    """
    Return (ok, warnings) after checking repo size and content.
    ok=False means the repo cannot become a dungeon.
    warnings is a list of yellow-note strings.
    Implemented in Step 2.
    """
    raise NotImplementedError("repo_check.playability_check — implemented in Step 2")
