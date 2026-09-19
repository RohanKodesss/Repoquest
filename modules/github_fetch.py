"""
github_fetch.py — GitHub REST API client.

All HTTP requests use requests.get with timeout=10.
Uses GITHUB_TOKEN from environment if set.
"""

from __future__ import annotations
import base64
import json
import os
import re
import requests

API_BASE = "https://api.github.com"
TIMEOUT = 10


class GitHubFetchError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


def _headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token and token.strip() and token != "your_github_token_here":
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers


def fetch_repo_info(owner: str, repo: str) -> dict:
    """
    Fetch repository info from GET /repos/{owner}/{repo}.
    Returns repo metadata dict.
    Raises GitHubFetchError on 404, 403/429, network failure.
    """
    url = f"{API_BASE}/repos/{owner}/{repo}"
    try:
        res = requests.get(url, headers=_headers(), timeout=TIMEOUT)
    except requests.RequestException:
        raise GitHubFetchError(
            "network_fail", "Cannot reach GitHub. Check your connection.", 502
        )

    if res.status_code == 200:
        return res.json()
    elif res.status_code == 404:
        raise GitHubFetchError(
            "repo_not_found", "Repo not found or private. Public repos only.", 404
        )
    elif res.status_code in (403, 429):
        raise GitHubFetchError(
            "rate_limited", "GitHub rate limit hit. Try the demo repo instead.", 429
        )
    else:
        raise GitHubFetchError(
            "network_fail", f"GitHub returned HTTP status {res.status_code}.", 502
        )


def fetch_tree(owner: str, repo: str, branch: str) -> tuple[list[dict], bool]:
    """
    Fetch file tree recursively via GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1.
    Returns (tree_items, is_truncated).
    """
    url = f"{API_BASE}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        res = requests.get(url, headers=_headers(), timeout=TIMEOUT)
    except requests.RequestException:
        raise GitHubFetchError(
            "network_fail", "Cannot reach GitHub. Check your connection.", 502
        )

    if res.status_code != 200:
        return [], False

    data = res.json()
    tree = data.get("tree", [])
    truncated = data.get("truncated", False)
    return tree, truncated


def fetch_readme(owner: str, repo: str) -> str:
    """
    Fetch and decode README content from GET /repos/{owner}/{repo}/readme.
    Returns decoded text string, or empty string if missing.
    """
    url = f"{API_BASE}/repos/{owner}/{repo}/readme"
    try:
        res = requests.get(url, headers=_headers(), timeout=TIMEOUT)
        if res.status_code == 200:
            content_b64 = res.json().get("content", "")
            return base64.b64decode(content_b64).decode("utf-8", errors="replace")
    except requests.RequestException:
        pass
    return ""


def fetch_issues(owner: str, repo: str) -> list[dict]:
    """
    Fetch open issues via GET /repos/{owner}/{repo}/issues?state=open&per_page=30.
    Filters out pull requests (items containing 'pull_request' key).
    """
    url = f"{API_BASE}/repos/{owner}/{repo}/issues?state=open&per_page=30"
    try:
        res = requests.get(url, headers=_headers(), timeout=TIMEOUT)
        if res.status_code == 200:
            raw_issues = res.json()
            clean_issues = []
            for item in raw_issues:
                if "pull_request" not in item:
                    clean_issues.append(
                        {
                            "number": item.get("number"),
                            "title": item.get("title", ""),
                            "url": item.get("html_url", ""),
                            "body": item.get("body", "") or "",
                            "labels": [
                                l.get("name", "")
                                for l in item.get("labels", [])
                                if isinstance(l, dict)
                            ],
                        }
                    )
            return clean_issues
    except requests.RequestException:
        pass
    return []


def _parse_requirements_txt(content: str) -> list[str]:
    deps = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        pkg = re.split(r"[=><!~;]", line)[0].strip()
        if pkg:
            deps.append(pkg)
    return deps


def _parse_package_json(content: str) -> list[str]:
    deps = []
    try:
        data = json.loads(content)
        all_deps = {}
        all_deps.update(data.get("dependencies", {}))
        all_deps.update(data.get("devDependencies", {}))
        deps = list(all_deps.keys())
    except json.JSONDecodeError:
        pass
    return deps


def fetch_dependency_file(owner: str, repo: str) -> tuple[list[str] | None, str | None]:
    """
    Try requirements.txt then package.json.
    Returns (dependency_names, filename) or (None, None).
    """
    # 1. Try requirements.txt
    url_req = f"{API_BASE}/repos/{owner}/{repo}/contents/requirements.txt"
    try:
        res = requests.get(url_req, headers=_headers(), timeout=TIMEOUT)
        if res.status_code == 200:
            b64 = res.json().get("content", "")
            text = base64.b64decode(b64).decode("utf-8", errors="replace")
            deps = _parse_requirements_txt(text)
            return deps, "requirements.txt"
    except requests.RequestException:
        pass

    # 2. Try package.json
    url_pkg = f"{API_BASE}/repos/{owner}/{repo}/contents/package.json"
    try:
        res = requests.get(url_pkg, headers=_headers(), timeout=TIMEOUT)
        if res.status_code == 200:
            b64 = res.json().get("content", "")
            text = base64.b64decode(b64).decode("utf-8", errors="replace")
            deps = _parse_package_json(text)
            return deps, "package.json"
    except requests.RequestException:
        pass

    return None, None
