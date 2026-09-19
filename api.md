# RepoQuest REST API Specification

**Based on:** Spec v5.1  
**Revision:** 4 (final)

---

## 1. Overview and Conventions

| Item | Rule |
|---|---|
| **Base URL** | `http://localhost:5000` |
| **Format** | Requests and responses are JSON, except `GET /` (HTML) |
| **Request header** | `Content-Type: application/json` on every POST |
| **Authentication** | None. `GITHUB_TOKEN` and `GEMINI_API_KEY` live in `.env` |
| **CORS** | Not needed (same-origin Flask server) |
| **State** | Server is stateless. State saved in `cache/owner-repo.json` |
| **Error shape** | Standard JSON shape for all API errors |

### Endpoint Summary
| # | Method | URL | Job |
|---|---|---|---|
| 1 | `GET` | `/` | Serves `templates/index.html` |
| 2 | `POST` | `/api/check` | Validates URL, checks cache, fetches repo data, builds map, returns traffic light |
| 3 | `POST` | `/api/start` | Adds narration + quiz to saved map, returns full game JSON |

---

## 2. Endpoints

### 2.1 GET /
Returns `templates/index.html`.

### 2.2 POST /api/check

**Request Body:**
```json
{
  "url": "github.com/owner/repo"
}
```

**Success Response (Green/Yellow - HTTP 200):**
```json
{
  "status": "green",
  "owner": "pallets",
  "repo": "flask",
  "language": "Python",
  "rooms": 12,
  "monsters": 1,
  "keys": 0,
  "warnings": ["No dependency file found. This dungeon has no keys."],
  "message": "Playable. 12 rooms, 1 monsters, 0 keys.",
  "cached": false
}
```

**Cached Response (HTTP 200):**
```json
{
  "status": "green",
  "owner": "pallets",
  "repo": "flask",
  "language": "Python",
  "rooms": 12,
  "monsters": 1,
  "keys": 0,
  "warnings": [],
  "message": "Loaded from cache.",
  "cached": true
}
```

**Error Responses:**
- `400 bad_request`: Missing/invalid JSON body
- `400 bad_format`: Invalid URL pattern
- `404 repo_not_found`: Repo missing or private
- `422 empty_repo`: Repo has no files
- `422 too_small`: Fewer than 5 files or 2 folders
- `422 map_failed`: Connectivity check failed
- `429 rate_limited`: GitHub API rate limit hit
- `502 network_fail`: Cannot reach GitHub

---

### 2.3 POST /api/start

**Request Body:**
```json
{
  "url": "github.com/owner/repo"
}
```

**Precondition:** `/api/check` must have succeeded for this repo.  
**Response (HTTP 200):** Returns the full game object schema.

**Error Responses:**
- `400 bad_request`: Missing/invalid JSON body
- `400 bad_format`: Invalid URL pattern
- `409 not_checked`: No saved map found for repo

---

## 3. Game Object Schema

```json
{
  "repo": "owner/repo",
  "language": "Python",
  "warnings": [],
  "start": "readme-hall",
  "boss": "room-src-flask",
  "rooms": {
    "readme-hall": {
      "folder": "",
      "exits": ["room-src-flask"],
      "keys": [],
      "monsters": []
    },
    "room-src-flask": {
      "folder": "src/flask",
      "exits": ["readme-hall"],
      "keys": [],
      "monsters": ["issue-6146"]
    }
  },
  "monsters": {
    "issue-6146": {
      "kind": "issue",
      "title": "Add Cloudflare to Flask Hosting Platforms docs?",
      "url": "https://github.com/pallets/flask/issues/6146",
      "placed_by": "keyword",
      "file": null
    }
  },
  "keys": {},
  "narration": {
    "rooms": {
      "readme-hall": "You are in the entrance hall. Look around — exits lead onward.",
      "room-src-flask": "You are in src/flask. Look around — exits lead onward."
    },
    "monsters": {
      "issue-6146": "A creature blocks the way: Add Cloudflare to Flask Hosting Platforms docs?."
    },
    "keys": {}
  },
  "narrated_by": "template",
  "quiz": {
    "monsters": {
      "issue-6146": {
        "question": "Which room holds `src/flask/__init__.py`?",
        "options": ["room-src-flask", "readme-hall", "room-tests"],
        "answer": "room-src-flask"
      }
    },
    "boss": [
      {
        "question": "Which room holds `src/flask/app.py`?",
        "options": ["room-src-flask", "readme-hall"],
        "answer": "room-src-flask"
      }
    ]
  }
}
```

---

## 4. Standard Error Format

```json
{
  "status": "red",
  "error": "error_code",
  "message": "Human readable error description",
  "suggestion": "Optional suggestion text"
}
```
