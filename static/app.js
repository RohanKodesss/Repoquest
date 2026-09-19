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
  visitedRooms: new Set(),
  defeatedMonsters: 0,
  bossQuestionIndex: 0,
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
  addElement(box, "p", `❌ ${message}`, "error-msg");
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
    state.visitedRooms = new Set([state.currentRoom]);
    state.defeatedMonsters = 0;
    state.bossQuestionIndex = 0;

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
  state.visitedRooms.add(state.currentRoom);
  const roomData = state.game.rooms[state.currentRoom];
  if (!roomData) return;

  // Check if entering boss room
  if (state.currentRoom === state.game.boss) {
    startBossFight();
    return;
  }

  // 1. Top HUD
  const hud = addElement(gameScreen, "div", null, null);
  hud.id = "hud";
  addElement(hud, "span", `❤️ ${state.health}`, "red");
  addElement(hud, "span", `⭐ ${state.score}`, "yellow");
  if (state.inventory.length > 0) {
    addElement(hud, "span", `🎒 [ ${state.inventory.join(", ")} ]`, "dim");
  }

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
      const isBossExit = exitId === state.game.boss;
      const prefix = isBossExit ? "👑 BOSS → " : "→ ";
      const btnText = `${prefix}${exitFolder || "readme-hall"}`;
      const btnClass = isBossExit ? "btn-danger" : "btn-secondary";
      const btn = addElement(exitsContainer, "button", btnText, btnClass);
      btn.addEventListener("click", () => {
        state.currentRoom = exitId;
        renderGame();
      });
    });
  } else {
    addElement(exitsContainer, "p", "No exits from here.", "dim");
  }

  // 5. Items Section (Keys)
  if (roomData.keys && roomData.keys.length > 0) {
    addElement(gameScreen, "div", "Items here:", "section-label");
    const itemsContainer = addElement(gameScreen, "div", null, null);
    roomData.keys.forEach((keyName) => {
      const keyBtn = addElement(itemsContainer, "button", `📦 ${keyName}`, "btn-secondary");
      keyBtn.addEventListener("click", () => {
        const index = roomData.keys.indexOf(keyName);
        if (index > -1) {
          roomData.keys.splice(index, 1);
        }
        state.inventory.push(keyName);
        state.score += 5;
        renderGame();
      });
    });
  }

  // 6. Monsters Section
  if (roomData.monsters && roomData.monsters.length > 0) {
    addElement(gameScreen, "div", "Monsters:", "section-label");
    const monstersContainer = addElement(gameScreen, "div", null, null);
    roomData.monsters.forEach((monsterId) => {
      const monster = state.game.monsters[monsterId];
      if (!monster) return;

      const card = addElement(monstersContainer, "div", null, "monster-card");

      const headerText = monster.kind === "issue"
        ? `👹 Issue: ${monster.title}`
        : `👹 ${monster.title}`;

      addElement(card, "div", headerText, "monster-title");
      addElement(card, "span", `placed by: ${monster.placed_by}`, "badge");

      if (monster.url) {
        const link = addElement(card, "a", "[ Open on GitHub ]", "issue-link");
        link.href = monster.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      } else if (monster.file) {
        addElement(card, "div", `Guarding: ${monster.file}`, "dim");
      }

      const fightBtn = addElement(card, "button", "Fight Monster", "btn-danger");
      fightBtn.addEventListener("click", () => startMonsterFight(monsterId));
    });
  }
}

function startMonsterFight(monsterId) {
  hideAllScreens();
  fightScreen.style.display = "block";
  renderFightScreen(monsterId, null);
}

function renderFightScreen(monsterId, statusMessage) {
  clearElement(fightScreen);

  const monster = state.game.monsters[monsterId];
  const qData = state.game.quiz && state.game.quiz.monsters && state.game.quiz.monsters[monsterId];

  // HUD
  const hud = addElement(fightScreen, "div", null, null);
  hud.id = "hud";
  addElement(hud, "span", `❤️ ${state.health}`, "red");
  addElement(hud, "span", `⭐ ${state.score}`, "yellow");

  // Container
  const card = addElement(fightScreen, "div", null, "fight-card");
  const headerText = monster.kind === "issue"
    ? `👹 Issue: ${monster.title}`
    : `👹 ${monster.title}`;
  addElement(card, "h2", headerText, "monster-title");

  if (monster.url) {
    const link = addElement(card, "a", "[ Open on GitHub ]", "issue-link");
    link.href = monster.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  }

  if (statusMessage) {
    addElement(card, "p", statusMessage.text, statusMessage.type);
  }

  if (!qData) {
    addElement(card, "p", "No quiz question available.", "dim");
    const backBtn = addElement(card, "button", "Return to Room", "btn-secondary");
    backBtn.addEventListener("click", () => {
      hideAllScreens();
      gameScreen.style.display = "block";
      renderGame();
    });
    return;
  }

  // Question Text
  addElement(card, "p", qData.question, "question");

  // Options
  const optsContainer = addElement(card, "div", null, null);
  qData.options.forEach((optId) => {
    const optRoom = state.game.rooms[optId];
    const optFolder = optRoom ? (optRoom.folder || "README HALL") : optId;
    const optBtn = addElement(optsContainer, "button", optFolder, "btn-secondary");

    optBtn.addEventListener("click", () => {
      if (optId === qData.answer) {
        state.score += 10;
        state.defeatedMonsters += 1;
        const currentRoomData = state.game.rooms[state.currentRoom];
        if (currentRoomData && currentRoomData.monsters) {
          const idx = currentRoomData.monsters.indexOf(monsterId);
          if (idx > -1) {
            currentRoomData.monsters.splice(idx, 1);
          }
        }
        hideAllScreens();
        gameScreen.style.display = "block";
        renderGame();
      } else {
        state.health -= 20;
        if (state.health <= 0) {
          state.health = 0;
          renderEndScreen(false);
        } else {
          renderFightScreen(monsterId, {
            text: "❌ Wrong answer! You lost 20 health. Try again.",
            type: "red"
          });
        }
      }
    });
  });

  const fleeBtn = addElement(card, "button", "Flee", "btn-secondary");
  fleeBtn.addEventListener("click", () => {
    hideAllScreens();
    gameScreen.style.display = "block";
    renderGame();
  });
}

function startBossFight() {
  hideAllScreens();
  fightScreen.style.display = "block";
  renderBossFightScreen(null);
}

function renderBossFightScreen(statusMessage) {
  clearElement(fightScreen);

  const bossRoom = state.game.rooms[state.game.boss];
  const bossFolder = bossRoom ? (bossRoom.folder || "README HALL") : state.game.boss;
  const bossQuestions = state.game.quiz && state.game.quiz.boss ? state.game.quiz.boss : [];
  const qData = bossQuestions[state.bossQuestionIndex];

  // HUD
  const hud = addElement(fightScreen, "div", null, null);
  hud.id = "hud";
  addElement(hud, "span", `❤️ ${state.health}`, "red");
  addElement(hud, "span", `⭐ ${state.score}`, "yellow");

  const card = addElement(fightScreen, "div", null, "fight-card");
  addElement(card, "h2", `🏆 BOSS FIGHT: ${bossFolder.toUpperCase()}`, "monster-title");
  addElement(
    card,
    "div",
    `Question ${state.bossQuestionIndex + 1} of ${bossQuestions.length}`,
    "badge"
  );

  if (statusMessage) {
    addElement(card, "p", statusMessage.text, statusMessage.type);
  }

  if (!qData) {
    // If questions finished or missing
    state.score += 50;
    renderEndScreen(true);
    return;
  }

  addElement(card, "p", qData.question, "question");

  const optsContainer = addElement(card, "div", null, null);
  qData.options.forEach((optId) => {
    const optRoom = state.game.rooms[optId];
    const optFolder = optRoom ? (optRoom.folder || "README HALL") : optId;
    const optBtn = addElement(optsContainer, "button", optFolder, "btn-secondary");

    optBtn.addEventListener("click", () => {
      if (optId === qData.answer) {
        state.bossQuestionIndex += 1;
        if (state.bossQuestionIndex >= bossQuestions.length) {
          // Defeated boss! +50 score
          state.score += 50;
          renderEndScreen(true);
        } else {
          renderBossFightScreen({
            text: "✅ Correct answer! Next question...",
            type: "green"
          });
        }
      } else {
        state.health -= 20;
        if (state.health <= 0) {
          state.health = 0;
          renderEndScreen(false);
        } else {
          renderBossFightScreen({
            text: "❌ Wrong answer! You lost 20 health. Try again.",
            type: "red"
          });
        }
      }
    });
  });
}

function renderEndScreen(isVictory) {
  hideAllScreens();
  endScreen.style.display = "block";
  clearElement(endScreen);

  const card = addElement(endScreen, "div", null, "end-card");

  if (isVictory) {
    addElement(card, "h2", "🏆 You defeated the Boss!", "green");
  } else {
    addElement(card, "h2", "💀 Defeated in the Dungeon!", "red");
  }

  addElement(card, "p", `Final Score: ${state.score}`, "status-line");

  addElement(card, "div", "What you learned:", "section-label");
  const learnedList = addElement(card, "ul", null, "learned");

  addElement(
    learnedList,
    "li",
    `Visited ${state.visitedRooms.size} of ${Object.keys(state.game.rooms).length} rooms`
  );
  addElement(learnedList, "li", `Collected ${state.inventory.length} keys`);
  addElement(learnedList, "li", `Defeated ${state.defeatedMonsters} monsters`);

  const bossRoom = state.game.rooms[state.game.boss];
  const bossFolder = bossRoom ? (bossRoom.folder || "README HALL") : state.game.boss;
  addElement(learnedList, "li", `Reached the boss: ${bossFolder}`);

  const btnRow = addElement(card, "div", null, "input-row");
  btnRow.style.marginTop = "20px";

  const againBtn = addElement(btnRow, "button", "Play Again");
  againBtn.addEventListener("click", () => {
    state.currentRoom = state.game.start || "readme-hall";
    state.health = 100;
    state.score = 0;
    state.inventory = [];
    state.visitedRooms = new Set([state.currentRoom]);
    state.defeatedMonsters = 0;
    state.bossQuestionIndex = 0;
    hideAllScreens();
    gameScreen.style.display = "block";
    renderGame();
  });

  const newRepoBtn = addElement(btnRow, "button", "Try Another Repo", "btn-secondary");
  newRepoBtn.addEventListener("click", () => {
    hideAllScreens();
    startScreen.style.display = "block";
    repoUrlInput.value = "";
    clearElement(checkScreen);
  });
}
