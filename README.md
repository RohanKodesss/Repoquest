<p align="center">
  <img src="static/logo.svg" alt="RepoQuest logo" width="360">
</p>

<h1 align="center">RepoQuest</h1>

<p align="center"><strong>Turn a public GitHub repository into a short, verifiable learning adventure.</strong></p>

<p align="center">Code decides facts. AI tells the story.</p>

---

## Why RepoQuest?

Joining an unfamiliar codebase can be slow and intimidating. A repository tree
does not explain where to begin or how the pieces relate, while AI explanations
can confidently mention files that do not exist.

RepoQuest makes the first few minutes of exploration active and checkable.

| Repository fact | Game element |
|---|---|
| Folder structure | Rooms and exits |
| Dependencies | Keys to collect |
| Open GitHub issues | Monsters to investigate |
| Largest code area | Boss encounter |
| Repository description | Plain-English learning recap |

The map is built entirely by code from GitHub data. Gemini may add atmosphere,
but every backticked or path-like repository name in its narration is checked
against the real repository. If narration is unavailable or fails validation,
RepoQuest continues with safe template text.

## Highlights

- **A verifiable map:** Rooms, monsters, keys, and the boss come from actual
  repository data—not invented by a model.
- **Safe AI narration:** Generated names are validated once; a failed retry
  falls back to templates rather than showing unverified text.
- **A playable onboarding flow:** Explore, collect keys, answer quizzes, and
  defeat the boss in a browser-based text adventure.
- **Plain-English completion recap:** “What you learned” describes the
  project’s purpose and your progress without dumping folders or file paths.
- **Useful failure modes:** Clear traffic-light feedback for invalid URLs,
  private repositories, small repositories, rate limits, and network failures.
- **Works without Gemini:** Narration is optional; game play and quizzes remain
  available when no Gemini key is configured.
- **Vercel-aware caching:** Bundled demo games are readable after cold starts;
  a fresh serverless instance rebuilds a requested map when its temporary cache
  is empty.

## Quick start

### Requirements

- Python 3.12 or newer
- A GitHub token is recommended for reliable GitHub API access
- A Gemini API key is optional and only enables AI narration

```bash
git clone https://github.com/RohanKodesss/Repoquest.git
cd Repoquest

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
flask --app app run --debug
```

Open `http://127.0.0.1:5000`, then try `github.com/pallets/flask`.

### Environment variables

| Variable | Required | Purpose |
|---|---:|---|
| `GITHUB_TOKEN` | Recommended | Raises GitHub API limits for public-repository checks |
| `GEMINI_API_KEY` | No | Enables Gemini narration |
| `GEMINI_MODEL` | No | Overrides the default Gemini model |
| `REPOQUEST_CACHE_DIR` | No | Overrides the runtime cache directory on Vercel |

Never commit `.env`; it is already ignored by Git.

## How a game is built

```text
Paste a GitHub URL
        |
Validate URL and load a cached map when available
        |
Fetch repository metadata, tree, README, issues, and dependencies
        |
Build and validate a connected game map with deterministic code
        |
Generate optional narration and validate repository names
        |
Create quizzes from real map facts and start the adventure
```

The frontend keeps the player’s score, inventory, and room progress in the
browser. The server cache stores game maps only; it is not a database or a
multi-user session system.

## Architecture

```text
Browser
  index.html + app.js + style.css
          |
          | POST /api/check and POST /api/start
          v
Flask application (app.py)
  repo check -> GitHub fetch -> map builder -> cache
                               |
                               v
                    narration + validation -> quiz builder
```

| Module | Responsibility |
|---|---|
| `repo_check.py` | Parses GitHub URLs and checks whether a repository is playable |
| `github_fetch.py` | Calls the GitHub REST API with timeouts and safe error handling |
| `map_builder.py` | Creates rooms, exits, keys, monsters, boss, and project summary data |
| `name_validator.py` | Rejects generated repository names that are not real |
| `narrator.py` | Gemini narration with retry and template fallback |
| `quiz.py` | Builds deterministic questions from map facts |
| `cache.py` | Uses local disk in development and `/tmp` on Vercel |

## Run tests

```bash
python -m pytest -v
```

The tests cover map connectivity, guardian-monster fallback, and name
validation. They do not call GitHub or Gemini.

## Deploy to Vercel

RepoQuest deploys as one Flask application—there is no separate frontend or
CORS configuration to maintain.

1. Import the repository into [Vercel](https://vercel.com/new).
2. Keep the default build settings; Vercel detects the `app` object in `app.py`.
3. Add `GITHUB_TOKEN` in **Settings → Environment Variables**. Add
   `GEMINI_API_KEY` and optionally `GEMINI_MODEL` for AI narration.
4. Deploy.

Vercel’s application filesystem is read-only. RepoQuest reads included demo
maps from the deployment bundle and writes transient maps to `/tmp`. That cache
can disappear after a cold start; the start endpoint rebuilds a missing map
instead of failing.

## Honest limits

- Public GitHub repositories only.
- Large repositories are reduced to at most 12 rooms.
- Issue-to-room placement is a heuristic based on mentions, labels, and
  keywords; it is not a claim that an issue belongs to a specific file.
- The validator verifies names and path-like tokens, not every factual claim in
  prose.
- A Vercel runtime cache is temporary. Use durable storage before adding
  accounts, shared progress, or long-term saved games.

## Documentation

- [API reference](api.md)
- [Live-demo script](DEMO_SCRIPT.md)
- [MIT License](LICENSE)
