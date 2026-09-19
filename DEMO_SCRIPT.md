# RepoQuest — 90-Second Stage Script

**Target Time:** 90 seconds  
**Driver:** You drive. Do not hand over the keyboard during the pitch.  
**Primary Demo URL:** `github.com/pallets/flask`

---

## 1. Pitch (15s)
> "Onboarding to an unfamiliar codebase is slow, boring, and overwhelming. We turned it into a playable game.  
> The core principle: **Code decides facts. AI tells the story.**  
> Every room is a real folder, every monster is a real open issue, and the AI is physically incapable of hallucinating a file name."

---

## 2. Show a Bad URL (10s)
1. Type `github.com/notreal/notreal` in the input box.
2. Click **Check Repo**.
3. **Show the Red Error Card:**  
   > *"Repo not found or private. Public repos only."*
4. Point out: *"We validate format and existence before building anything."*

---

## 3. Show a Real Repo (10s)
1. Click the demo link or paste `github.com/pallets/flask` (with the `github.com/` prefix).
2. Click **Check Repo**.
3. **Show the Green/Yellow Scan Card:**  
   > *"Playable. 12 rooms, 1 monsters, 0 keys."*
4. Point out: *"Built deterministically from GitHub's tree and issue data."*

---

## 4. Play 3 Rooms & Fight a Monster (30s)
1. Click **Start Game**.
2. **Room 1 (README Hall):** Show room title, template/AI narration text, and exits.
3. Click exit: **`→ src/flask`**.
4. Click exit: **`→ tests`**.
5. Click **Fight Monster** on `Issue #6146: Add Cloudflare to Flask Hosting Platforms docs?`.
6. Click **`[ Open on GitHub ]`** to open the real GitHub issue in a new tab.
7. Answer the quiz question correctly (**`room-docs`**).
8. Show score incrementing by **+10** and the monster disappearing.

---

## 5. Show Proof (15s)
1. Open terminal tab alongside browser.
2. Run:
   ```bash
   python -m pytest tests/test_validator.py -v
   ```
3. Show all 5 tests passing:  
   > *"Our validator extracts every backticked token and path-like token and checks it against a set of everything real in the repository. Fake names trigger plain template fallback."*

---

## 6. Close (10s)
> "Every room is a real folder. Every monster is a real issue. The game plays offline, works without AI, and no hallucinated filename can survive. Thank you!"

---

## Backup Plan
- **Wi-Fi Dies during demo:** The pre-cached file `cache/pallets-flask.json` loads instantly and plays offline without AI or network access.
- **App Crashes:** Play `demo_backup.mp4`.
- **Judge asks to try:** Hand over keyboard AFTER the pitch is complete.
