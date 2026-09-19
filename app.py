from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

from modules import cache, github_fetch, map_builder, narrator, quiz, repo_check

load_dotenv()

app = Flask(__name__)


def _error_response(error_code: str, message: str, status_code: int, suggestion: str = None):
    payload = {
        "status": "red",
        "error": error_code,
        "message": message,
    }
    if suggestion:
        payload["suggestion"] = suggestion
    return jsonify(payload), status_code


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def check_repo():
    """
    Repo check endpoint.
    1. Validates URL format.
    2. Checks cache first (returns cached summary without network call).
    3. Fetches repo info, tree, README, issues, dependency file from GitHub.
    4. Runs playability check.
    5. Builds map, checks connectivity, saves to cache.
    6. Returns traffic light + counts.
    """
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or "url" not in body or not isinstance(body.get("url"), str):
        return _error_response(
            "bad_request",
            'Send JSON like {"url": "github.com/owner/repo"}.',
            400
        )

    parsed = repo_check.parse_repo_url(body.get("url", ""))
    if parsed is None:
        return _error_response(
            "bad_format",
            "That doesn't look like a GitHub URL. Try github.com/owner/repo.",
            400
        )

    owner, repo = parsed

    # 1. Check cache first
    cached_game = cache.load(owner, repo)
    if cached_game is not None:
        warnings = cached_game.get("warnings", [])
        return jsonify({
            "status": "yellow" if warnings else "green",
            "owner": owner,
            "repo": repo,
            "language": cached_game.get("language", "Unknown"),
            "rooms": len(cached_game.get("rooms", {})),
            "monsters": len(cached_game.get("monsters", {})),
            "keys": len(cached_game.get("keys", {})),
            "warnings": warnings,
            "message": "Loaded from cache.",
            "cached": True
        }), 200

    # 2. Fetch repo info from GitHub
    try:
        repo_info = github_fetch.fetch_repo_info(owner, repo)
    except github_fetch.GitHubFetchError as err:
        return _error_response(
            err.error_code,
            err.message,
            err.status_code,
            suggestion="Try the demo repo instead." if err.status_code in (403, 429) else None
        )

    branch = repo_info.get("default_branch", "main")
    language = repo_info.get("language", "Unknown") or "Unknown"

    # 3. Fetch tree, readme, issues, dependencies
    try:
        tree, is_truncated = github_fetch.fetch_tree(owner, repo, branch)
        readme = github_fetch.fetch_readme(owner, repo)
        issues = github_fetch.fetch_issues(owner, repo)
        dependencies, dep_filename = github_fetch.fetch_dependency_file(owner, repo)
    except github_fetch.GitHubFetchError as err:
        return _error_response(err.error_code, err.message, err.status_code)

    # 4. Playability check
    ok, warnings, error_info = repo_check.playability_check(tree, issues, dependencies)
    if not ok and error_info:
        err_code, err_msg, err_status = error_info
        return _error_response(err_code, err_msg, err_status)

    if is_truncated:
        warnings.append("Repo file tree was truncated by GitHub API; dungeon built from available files.")

    # 5. Build Map
    repo_data = {
        "owner": owner,
        "repo": repo,
        "language": language,
        "description": repo_info.get("description") or "",
        "readme": readme,
        "tree": tree,
        "issues": issues,
        "dependencies": dependencies or [],
        "dep_filename": dep_filename,
        "warnings": warnings,
    }

    try:
        game_map = map_builder.build_map(repo_data)
    except ValueError:
        return _error_response(
            "map_failed",
            "Couldn't build a dungeon for this repo. Try another one.",
            422
        )

    # 6. Save map to cache
    cache.save(owner, repo, game_map)

    room_count = len(game_map["rooms"])
    monster_count = len(game_map["monsters"])
    key_count = len(game_map["keys"])

    msg = f"Playable. {room_count} rooms, {monster_count} monsters, {key_count} keys." if warnings else f"Ready. {room_count} rooms, {monster_count} monsters, {key_count} keys."

    return jsonify({
        "status": "yellow" if warnings else "green",
        "owner": owner,
        "repo": repo,
        "language": language,
        "rooms": room_count,
        "monsters": monster_count,
        "keys": key_count,
        "warnings": warnings,
        "message": msg,
        "cached": False
    }), 200


@app.route("/api/start", methods=["POST"])
def start_game():
    """
    Start game endpoint.
    1. Validates URL format.
    2. Loads saved map from cache.
    3. Populates template narration if missing.
    4. Populates quiz questions if missing.
    5. Saves updated game to cache.
    6. Returns full game JSON object.
    """
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or "url" not in body or not isinstance(body.get("url"), str):
        return _error_response(
            "bad_request",
            'Send JSON like {"url": "github.com/owner/repo"}.',
            400
        )

    parsed = repo_check.parse_repo_url(body.get("url", ""))
    if parsed is None:
        return _error_response(
            "bad_format",
            "That doesn't look like a GitHub URL. Try github.com/owner/repo.",
            400
        )

    owner, repo = parsed
    game = cache.load(owner, repo)

    if game is None:
        return _error_response(
            "not_checked",
            "Check the repo first.",
            409
        )

    # 1. Fill narration template if missing
    if game.get("narration") is None:
        game = narrator.fill_templates(game)

    # 2. Fill quiz if missing
    if game.get("quiz") is None:
        game["quiz"] = quiz.generate_quiz(game)

    cache.save(owner, repo, game)
    return jsonify(game), 200


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(port=5000, debug=debug)
