/* =========================================================
   RepoQuest — Frontend Logic
   Rule: repo text is always set via element.textContent, never innerHTML.
   ========================================================= */

// Game state lives in the browser
const state = {
  game: null,
  currentRoom: null,
  health: 100,
  score: 0,
  inventory: []
};

// DOM elements
const startScreen = document.getElementById("start-screen");
const checkScreen = document.getElementById("check-screen");
const loadingScreen = document.getElementById("loading-screen");
const errorScreen = document.getElementById("error-screen");
const gameScreen = document.getElementById("game-screen");
const fightScreen = document.getElementById("fight-screen");
const endScreen = document.getElementById("end-screen");
const repoUrlInput = document.getElementById("repo-url");
const checkBtn = document.getElementById("check-btn");
const demoLink = document.getElementById("demo-link");

// Helper: safe text element creation
function addElement(parent, tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined && text !== null) {
    el.textContent = text;
  }
  if (className) {
    el.className = className;
  }
  parent.appendChild(el);
  return el;
}

// Helper: clear element content
function clearElement(el) {
  el.textContent = "";
}

// Event Listeners
if (demoLink) {
  demoLink.addEventListener("click", (e) => {
    e.preventDefault();
    repoUrlInput.value = "github.com/tiangolo/fastapi";
  });
}

if (checkBtn) {
  checkBtn.addEventListener("click", async () => {
    const url = repoUrlInput.value.trim();
    if (!url) return;

    // Show loading / clear previous status
    clearElement(checkScreen);
    checkScreen.style.display = "block";
    addElement(checkScreen, "p", "Checking repository...", "dim");

    try {
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      console.log("Check response:", data);
      
      clearElement(checkScreen);
      if (res.ok) {
        addElement(checkScreen, "p", data.message || "Repo checked", data.status || "green");
      } else {
        addElement(checkScreen, "p", data.message || "Error checking repo", "red");
      }
    } catch (err) {
      console.error("Fetch error:", err);
      clearElement(checkScreen);
      addElement(checkScreen, "p", "Cannot reach server", "red");
    }
  });
}
