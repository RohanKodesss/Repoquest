# RepoQuest Demo Script

**Target:** 90 seconds

**Demo repository:** `github.com/pallets/flask`
**Goal:** Show that RepoQuest makes codebase exploration engaging without
letting AI invent repository facts.

> Keep the demo conversational. Exact room, issue, and key counts can change
> as the source repository changes, so describe what appears instead of relying
> on fixed numbers.

## 1. Set the problem — 15 seconds

> “A new codebase can be overwhelming: a README tells you what a project is,
> but not where to start or how the parts connect. RepoQuest turns that first
> exploration into a playable learning journey.”

> “The important rule is simple: code decides facts; AI only tells the story.”

## 2. Prove the guardrails — 10 seconds

1. Enter `github.com/notreal/notreal`.
2. Select **Check Repo**.
3. Show the red error card.

> “We validate the input and repository existence before we build anything.
> Private and missing repositories do not become fictional dungeons.”

## 3. Build a real game — 15 seconds

1. Enter `github.com/pallets/flask` or choose the demo link.
2. Select **Check Repo**.
3. Point to the traffic-light result, room count, and any warnings.

> “The map is created from the actual GitHub tree, dependencies, and open
> issues. No model chooses the rooms or invents monsters.”

## 4. Play the learning flow — 30 seconds

1. Select **Start Game**.
2. Visit two or three rooms using the exits.
3. Collect a key if the game shows one.
4. Open an issue monster and use its GitHub link when available.
5. Answer a quiz question and show the score update.
6. Reach the boss when the route allows it.

> “The game turns exploration into feedback. You do not just read a folder
> tree—you form a mental model, test it, and make progress.”

## 5. Show the trust boundary — 10 seconds

Open `tests/test_validator.py` or run:

```bash
python -m pytest tests/test_validator.py -v
```

> “Narration may be creative, but names are not trusted. Backticked names and
> path-like tokens are checked against the repository. A failed validation gets
> one retry, then safe template text.”

## 6. End with the learning recap — 10 seconds

Finish or intentionally end the run to show **What you learned**.

> “The recap explains what the project does and what you explored in plain
> English. It does not make a beginner decode a list of internal file paths.”

> “RepoQuest makes the first ten minutes of onboarding active, memorable, and
> verifiable.”

## Demo resilience

| Situation | What to do |
|---|---|
| Gemini is unavailable | Continue—the template narrator keeps the game playable. |
| GitHub rate limit is reached | Use an included demo repository or set `GITHUB_TOKEN`. |
| A Vercel instance is cold | Start Game rebuilds a missing temporary map automatically. |
| Network is unavailable locally | Use a bundled demo map that has already been checked. |

Before presenting, run the test command once and open the app in the target
browser. Do not promise a specific issue, folder, or count from an external
repository; those facts naturally change over time.
