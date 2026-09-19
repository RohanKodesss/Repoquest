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
  inventory: [],
  currentUrl: ""
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

// Safe DOM element helper
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

// Clear element content
function clearElement(el) {
  el.textContent = "";
}

// Hide all screen divs
function hideAllScreens() {
  startScreen.style.display = "none";
  checkScreen.style.display = "none";
  loadingScreen.style.display = "none";
  errorScreen.style.display = "none";
  gameScreen.style.display = "none";
  fightScreen.style.display = "none";
  endScreen.style.display = "none";
}

// Event Listeners
if (demoLink) {
  demoLink.addEventListener("click", (e) => {
    e.preventDefault();
    repoUrlInput.value = "github.com/pallets/flask";
  });
}

if (checkBtn) {
  checkBtn.addEventListener("click", async () => {
    const url = repoUrlInput.value.trim();
    if (!url) return;
    state.currentUrl = url;

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
      renderCheckCard(data);
    } catch (err) {
      console.error("Fetch error:", err);
      clearElement(checkScreen);
      renderErrorCard("Cannot reach server", "Check your connection.");
    }
  });
}

function renderErrorCard(message, suggestion) {
  clearElement(errorScreen);
  errorScreen.style.display = "block";
  const box = addElement(errorScreen, "div", null, "error-box");
  addElement(box, "p", f"❌ {message}", "error-msg");
  if (suggestion) {
    addElement(box, "p", suggestion, "suggestion");
  }
}

function renderCheckCard(data) {
  clearElement(checkScreen);
  checkScreen.style.display = "block";

  if (data.status === "red") {
    const box = addElement(checkScreen, "div", null, "error-box");
    addElement(box, "p", `❌ ${data.message}`, "error-msg");
    if (data.suggestion) {
      addElement(box, "p", data.suggestion, "suggestion");
    }
    return;
  }

  const card = addElement(checkScreen, "div", null, "check-card");
  const icon = data.status === "green" ? "✅" : "⚠️";
  
  addElement(card, "div", `${icon} ${data.message}`, `status-line ${data.status}`);
  addElement(card, "div", `${data.owner}/${data.repo} · ${data.language}`, "dim");
  addElement(
    card,
    "div",
    `${data.rooms} rooms · ${data.monsters} monsters · ${data.keys} keys`,
    "counts"
  );

  if (data.warnings && data.warnings.length > 0) {
    const warnBox = addElement(card, "div", null, "warnings");
    data.warnings.forEach((w) => {
      addElement(warnBox, "p", `• ${w}`);
    });
  }

  const startBtn = addElement(card, "button", "Start Game");
  startBtn.addEventListener("click", () => startGame(state.currentUrl));
}

async function startGame(url) {
  hideAllScreens();
  loadingScreen.style.display = "block";

  try {
    const res = await fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    const data = await res.json();

    if (!res.ok) {
      hideAllScreens();
      startScreen.style.display = "block";
      renderErrorCard(data.message || "Failed to start game.", data.suggestion);
      return;
    }

    state.game = data;
    state.currentRoom = data.start || "readme-hall";
    state.health = 100;
    state.score = 0;
    state.inventory = [];

    hideAllScreens();
    gameScreen.style.display = "block";
    renderGame();
  } catch (err) {
    console.error("Start game error:", err);
    hideAllScreens();
    startScreen.style.display = "block";
    renderErrorCard("Failed to start game", "Server connection error.");
  }
}

function renderGame() {
  clearElement(gameScreen);
  const roomData = state.game.rooms[state.currentRoom];
  if (!roomData) return;

  // 1. Top HUD
  const hud = addElement(gameScreen, "div", null, null);
  hud.id = "hud";
  addElement(hud, "span", `❤️ ${state.health}`, "red");
  addElement(hud, "span", `⭐ ${state.score}`, "yellow");

  // 2. Room Title
  const folder = roomData.folder;
  const titleText = folder ? folder.toUpperCase() : "README HALL";
  addElement(gameScreen, "h2", titleText, "room-title");

  // 3. Room Narration Prose
  const narrationText =
    (state.game.narration && state.game.narration.rooms && state.game.narration.rooms[state.currentRoom]) ||
    `You stand in ${folder || "the entrance hall"}.`;
  addElement(gameScreen, "p", narrationText, "room-text");

  // 4. Exits Section
  addElement(gameScreen, "div", "Exits:", "section-label");
  const exitsContainer = addElement(gameScreen, "div", null, null);

  if (roomData.exits && roomData.exits.length > 0) {
    roomData.exits.forEach((exitId) => {
      const exitRoom = state.game.rooms[exitId];
      const exitFolder = exitRoom ? exitRoom.folder : exitId;
      const btnText = `→ ${exitFolder || "readme-hall"}`;
      const btn = addElement(exitsContainer, "button", btnText, "btn-secondary");
      btn.addEventListener("click", () => {
        state.currentRoom = exitId;
        renderGame();
      });
    });
  } else {
    addElement(exitsContainer, "p", "No exits from here.", "dim");
  }
}
