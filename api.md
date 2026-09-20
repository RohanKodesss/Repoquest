# RepoQuest API Reference

RepoQuest exposes a small same-origin JSON API used by the browser game. There
is no user authentication API: GitHub and Gemini credentials stay on the server
as environment variables.

## Conventions

| Item | Value |
|---|---|
| Local base URL | `http://127.0.0.1:5000` |
| Production base URL | Your Vercel deployment URL |
| Request format | JSON for `POST` endpoints |
| Content type | `application/json` |
| Browser state | Score, inventory, and progress live in the browser |
| Server cache | Game maps are JSON files; Vercel uses temporary `/tmp` storage |

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Returns the game page |
| `POST` | `/api/check` | Validates a repository and builds or loads its map |
| `POST` | `/api/start` | Loads or rebuilds a map, adds narration and quizzes, then returns the game |

## `POST /api/check`

Checks a public GitHub repository before the player starts. A cache hit avoids
external requests; otherwise the service fetches repository metadata, the file
tree, README, issues, and dependency data before building a connected map.

### Request

```json
{
  "url": "github.com/owner/repo"
}
```

HTTPS URLs, a `.git` suffix, and repository subpaths are accepted. The owner
and repository are extracted from the URL; arbitrary URLs are never fetched.

### Success response

```json
{
  "status": "green",
  "owner": "pallets",
  "repo": "flask",
  "language": "Python",
  "rooms": 12,
  "monsters": 4,
  "keys": 0,
  "warnings": [],
  "message": "Ready. 12 rooms, 4 monsters, 0 keys.",
  "cached": false
}
```

`status` is `green` when the map has no warnings and `yellow` when it is still
playable but lacks optional data, such as open issues or dependencies.

## `POST /api/start`

Returns a complete game object. Call it after `/api/check` for the fastest path.
If a Vercel cold start has cleared its temporary cache, this endpoint rebuilds
the map rather than returning a cache-miss error.

### Request

```json
{
  "url": "github.com/owner/repo"
}
```

### Response shape

```json
{
  "repo": "owner/repo",
  "language": "Python",
  "description": "A short plain-English explanation from the repository.",
  "warnings": [],
  "start": "readme-hall",
  "boss": "room-src",
  "rooms": {
    "readme-hall": {
      "folder": "",
      "exits": ["room-src"],
      "keys": [],
      "monsters": []
    }
  },
  "monsters": {},
  "keys": {},
  "narration": {
    "rooms": {},
    "monsters": {},
    "keys": {}
  },
  "narrated_by": "template",
  "quiz": {
    "monsters": {},
    "boss": []
  }
}
```

### Important response fields

| Field | Description |
|---|---|
| `description` | Repository description used for the plain-English learning recap |
| `rooms` | Connected game areas, each with exits, keys, and monsters |
| `monsters` | Open issues or guardian fallback encounters |
| `keys` | Dependencies collected during play |
| `narration` | Verified Gemini prose or safe template text |
| `narrated_by` | `llm`, `mixed`, or `template` |
| `quiz` | Question sets derived from real map facts |

Internal fields prefixed with `_` may be present for validation and caching.
Clients should treat them as implementation details.

## Error format

All handled API failures use the following shape:

```json
{
  "status": "red",
  "error": "error_code",
  "message": "Human-readable explanation.",
  "suggestion": "Optional next step."
}
```

| HTTP status | Error code | Meaning |
|---:|---|---|
| 400 | `bad_request` | The body is missing or does not contain a string `url` |
| 400 | `bad_format` | The URL is not a supported GitHub repository URL |
| 404 | `repo_not_found` | The repository is missing or private |
| 422 | `empty_repo` | The repository has no usable file tree |
| 422 | `too_small` | The repository has fewer than five files or two folders |
| 422 | `map_failed` | A connected game map could not be created |
| 429 | `rate_limited` | GitHub rejected the request because of rate limiting |
| 502 | `network_fail` | GitHub could not be reached or returned an unexpected response |

## Operational notes

- `GITHUB_TOKEN` is recommended to reduce rate-limit failures.
- `GEMINI_API_KEY` is optional. Without it, `narrated_by` is `template` and
  game play continues.
- Vercel’s `/tmp` cache is not durable. Build a database-backed cache before
  relying on a game map across long periods, regions, or users.
