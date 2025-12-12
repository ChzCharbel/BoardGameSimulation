// Variables globales
let simulationId = null;
let socket = null;
let currentState = null;
let autoRunning = false;

// Constantes
const FIRE_STATES = {
  0: "clear",
  1: "smoke",
  2: "fire",
};

const WALL_TYPES = {
  0: "none",
  1: "wall1",
  2: "wall2",
  3: "door-open",
  4: "door-closed",
};

// Inicialización
document.addEventListener("DOMContentLoaded", function () {
  initializeSimulation();
  setupEventListeners();
});

function initializeSimulation() {
  // Obtener simulation ID de la URL
  const urlParams = new URLSearchParams(window.location.search);
  simulationId = urlParams.get("id");

  if (!simulationId) {
    // Si no hay ID, crear nueva simulación
    createNewSimulation();
  } else {
    // Cargar simulación existente
    loadSimulation(simulationId);
  }

  // Inicializar WebSocket
  initializeSocket();
}

function setupEventListeners() {
  document.getElementById("step-btn").addEventListener("click", stepSimulation);
  document
    .getElementById("auto-btn")
    .addEventListener("click", toggleAutoSimulation);
  document
    .getElementById("stop-btn")
    .addEventListener("click", stopAutoSimulation);
  document
    .getElementById("reset-btn")
    .addEventListener("click", resetSimulation);
  document
    .getElementById("newGameBtn")
    .addEventListener("click", resetSimulation);
}

function initializeSocket() {
  socket = io();

  socket.on("connect", function () {
    console.log("Connected to server");
    if (simulationId) {
      socket.emit("join_simulation", { simulation_id: simulationId });
    }
  });

  socket.on("simulation_update", function (state) {
    updateDisplay(state);
  });

  socket.on("auto_status", function (data) {
    autoRunning = data.auto_running;
    updateControlButtons();
  });

  socket.on("joined_simulation", function (data) {
    console.log("Joined simulation:", data.simulation_id);
  });

  socket.on("error", function (data) {
    console.error("Socket error:", data.message);
    alert("Error: " + data.message);
  });
}

async function createNewSimulation() {
  try {
    const response = await fetch("/api/create_simulation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.simulation_id) {
      // Leave old simulation room if exists
      if (simulationId && socket) {
        socket.emit("leave_simulation", { simulation_id: simulationId });
      }
      
      simulationId = data.simulation_id;
      // Actualizar URL sin recargar la página
      history.pushState(null, "", `/simulation?id=${simulationId}`);
      
      // Join new simulation room for WebSocket updates
      if (socket) {
        socket.emit("join_simulation", { simulation_id: simulationId });
      }
      
      // Reset auto running state
      autoRunning = false;
      
      updateDisplay(data.state);
    } else {
      alert("Error al crear la simulación");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error al crear la simulación");
  }
}

async function loadSimulation(simId) {
  try {
    const response = await fetch(`/api/simulation/${simId}/state`);
    const data = await response.json();

    if (response.ok) {
      updateDisplay(data);
    } else {
      alert("Simulación no encontrada");
      createNewSimulation();
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error al cargar la simulación");
  }
}

async function stepSimulation() {
  if (!simulationId) return;

  try {
    const response = await fetch(`/api/simulation/${simulationId}/step`, {
      method: "POST",
    });

    const data = await response.json();

    if (data.success) {
      updateDisplay(data.state);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

async function toggleAutoSimulation() {
  if (!simulationId) return;

  if (autoRunning) {
    stopAutoSimulation();
  } else {
    startAutoSimulation();
  }
}

async function startAutoSimulation() {
  try {
    const response = await fetch(`/api/simulation/${simulationId}/auto_start`, {
      method: "POST",
    });

    if (response.ok) {
      autoRunning = true;
      updateControlButtons();
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

async function stopAutoSimulation() {
  try {
    const response = await fetch(`/api/simulation/${simulationId}/auto_stop`, {
      method: "POST",
    });

    if (response.ok) {
      autoRunning = false;
      updateControlButtons();
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

async function resetSimulation() {
  // Cerrar modal si está abierto
  const modal = bootstrap.Modal.getInstance(
    document.getElementById("gameOverModal")
  );
  if (modal) {
    modal.hide();
  }

  // Crear nueva simulación
  await createNewSimulation();
}

function updateControlButtons() {
  const autoBtn = document.getElementById("auto-btn");
  const stopBtn = document.getElementById("stop-btn");
  const stepBtn = document.getElementById("step-btn");

  if (autoRunning) {
    autoBtn.innerHTML = '<i class="fas fa-pause"></i> Auto (Running)';
    autoBtn.classList.remove("btn-outline-success");
    autoBtn.classList.add("btn-success");
    stopBtn.disabled = false;
    stepBtn.disabled = true;
  } else {
    autoBtn.innerHTML = '<i class="fas fa-play"></i> Auto';
    autoBtn.classList.remove("btn-success");
    autoBtn.classList.add("btn-outline-success");
    stopBtn.disabled = true;
    stepBtn.disabled = false;
  }

  // Disable all buttons if game is over
  if (currentState && currentState.game_over) {
    autoBtn.disabled = true;
    stopBtn.disabled = true;
    stepBtn.disabled = true;
  } else {
    autoBtn.disabled = false;
    if (!autoRunning) {
      stopBtn.disabled = true;
      stepBtn.disabled = false;
    }
  }
}

function updateDisplay(state) {
  currentState = state;

  // Actualizar estadísticas principales
  document.getElementById("round-count").textContent = state.round_count;
  document.getElementById("current-phase").textContent = translatePhase(
    state.phase
  );
  document.getElementById("rescued-count").textContent = state.rescued_victims;
  document.getElementById("lost-count").textContent = state.lost_victims;
  document.getElementById("damage-count").textContent = state.damage_count;
  document.getElementById("step-count").textContent = state.step_count;

  // Actualizar estadísticas de fuego
  document.getElementById("fire-count").textContent = state.stats.fire_count;
  document.getElementById("smoke-count").textContent = state.stats.smoke_count;
  document.getElementById("clear-count").textContent = state.stats.clear_count;

  // Actualizar tablero
  updateGameBoard(state);

  // Actualizar lista de agentes
  updateAgentsList(state.agents, state.current_agent_index);

  // Actualizar lista de POIs
  updatePOIsList(state.pois);

  // Update control buttons based on current state
  updateControlButtons();

  // Verificar fin del juego
  if (state.game_over) {
    autoRunning = false; // Stop auto if game ends
    showGameOverModal(state);
  }
}

function updateGameBoard(state) {
  const board = document.getElementById("game-board");
  board.innerHTML = "";

  const height = state.fire_states.length;
  const width = state.fire_states[0].length;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const cell = createCell(x, y, state);
      board.appendChild(cell);
    }
  }
}

function createCell(x, y, state) {
  const cell = document.createElement("div");
  cell.className = "cell";
  cell.id = `cell-${x}-${y}`;

  // Estado de fuego
  const fireState = state.fire_states[y][x];
  cell.classList.add(FIRE_STATES[fireState]);

  // Paredes
  const cellData = state.grid_data[y][x];
  addWallClasses(cell, cellData);

  // Agentes en esta celda
  const agentsInCell = state.agents.filter(
    (agent) => agent.pos && agent.pos[0] === x && agent.pos[1] === y
  );

  agentsInCell.forEach((agent, index) => {
    const agentElement = createAgentElement(
      agent,
      index,
      state.current_agent_index
    );
    cell.appendChild(agentElement);
  });

  // POIs en esta celda
  const poisInCell = state.pois.filter((poi) => poi.x === x && poi.y === y);
  poisInCell.forEach((poi) => {
    const poiElement = createPOIElement(poi);
    cell.appendChild(poiElement);
  });

  return cell;
}

function addWallClasses(cell, cellData) {
  // cellData es [top, right, bottom, left]
  const directions = ["top", "right", "bottom", "left"];

  cellData.forEach((wallType, index) => {
    const direction = directions[index];

    if (wallType === 1 || wallType === 2) {
      cell.classList.add(`wall-${direction}`);
    } else if (wallType === 3) {
      cell.classList.add(`door-${direction}`, "open");
    } else if (wallType === 4) {
      cell.classList.add(`door-${direction}`, "closed");
    }
  });
}

function createAgentElement(agent, index, currentAgentIndex) {
  const agentElement = document.createElement("div");
  agentElement.className = "agent";
  agentElement.textContent = agent.id;

  // Posición múltiple de agentes
  agentElement.style.left = `${2 + (index % 2) * 14}px`;
  agentElement.style.top = `${2 + Math.floor(index / 2) * 14}px`;

  // Rol del agente
  if (agent.carrying_victim) {
    agentElement.classList.add("carrying");
  } else if (agent.role === "rescuer") {
    agentElement.classList.add("rescuer");
  } else if (agent.role === "extinguisher") {
    agentElement.classList.add("extinguisher");
  }

  // Estado del agente
  if (agent.is_knocked_out) {
    agentElement.classList.add("knocked-out");
  }

  // Agente actual
  if (agent.id === currentAgentIndex) {
    agentElement.classList.add("current");
  }

  // Tooltip
  agentElement.title = `Agent ${agent.id} - ${agent.role || "No Role"} - AP: ${
    agent.action_points
  }`;

  return agentElement;
}

function createPOIElement(poi) {
  const poiElement = document.createElement("div");
  poiElement.className = "poi";
  poiElement.textContent = poi.id;

  if (poi.type === "victim") {
    poiElement.classList.add("victim");
  } else if (poi.type === "false") {
    poiElement.classList.add("false");
  }

  if (poi.revealed) {
    poiElement.classList.add("revealed");
  }

  poiElement.title = `POI ${poi.id} - ${poi.type} - ${
    poi.revealed ? "Revealed" : "Hidden"
  }`;

  return poiElement;
}

function updateAgentsList(agents, currentAgentIndex) {
  const agentsList = document.getElementById("agents-list");
  agentsList.innerHTML = "";

  agents.forEach((agent) => {
    const agentItem = document.createElement("div");
    agentItem.className = "agent-item";

    if (agent.id === currentAgentIndex) {
      agentItem.classList.add("current");
    }

    if (agent.is_knocked_out) {
      agentItem.classList.add("knocked-out");
    }

    agentItem.innerHTML = `
            <div>
                <span class="agent-id">Agent ${agent.id}</span>
                <div class="agent-role">${translateRole(agent.role)} ${
      agent.carrying_victim ? "👶" : ""
    }</div>
            </div>
            <div>
                <span class="agent-ap">${agent.action_points} AP</span>
            </div>
        `;

    agentsList.appendChild(agentItem);
  });
}

function updatePOIsList(pois) {
  const poisList = document.getElementById("pois-list");
  poisList.innerHTML = "";

  if (pois.length === 0) {
    poisList.innerHTML = '<div class="text-muted">No active POIs</div>';
    return;
  }

  pois.forEach((poi) => {
    const poiItem = document.createElement("div");
    poiItem.className = "poi-item";

    if (poi.type === "FALSE") {
      poiItem.classList.add("false");
    }

    if (poi.revealed) {
      poiItem.classList.add("revealed");
    }

    poiItem.innerHTML = `
            <div>
                <strong>POI ${poi.id}</strong>
                <small>(${poi.x}, ${poi.y})</small>
            </div>
            <div>
                <span class="badge ${
                  poi.type === "VICTIM" ? "bg-danger" : "bg-warning"
                }">
                    ${poi.type === "VICTIM" ? "Victim" : "False"}
                </span>
                ${poi.revealed ? "👁️" : "❓"}
            </div>
        `;

    poisList.appendChild(poiItem);
  });
}

function showGameOverModal(state) {
  const modal = new bootstrap.Modal(document.getElementById("gameOverModal"));
  const icon = document.getElementById("gameOverIcon");
  const reason = document.getElementById("gameOverReason");
  const stats = document.getElementById("gameOverStats");

  if (state.game_won) {
    icon.innerHTML = '<i class="fas fa-trophy fa-5x text-warning"></i>';
    reason.textContent = "Victory! " + state.end_reason;
    reason.className = "text-success";
  } else {
    icon.innerHTML = '<i class="fas fa-skull fa-5x text-danger"></i>';
    reason.textContent = "Defeat: " + state.end_reason;
    reason.className = "text-danger";
  }

  stats.innerHTML = `
        <div class="row">
            <div class="col-6">
                <h6>Victims Rescued</h6>
                <p class="h4 text-success">${state.rescued_victims}/7</p>
            </div>
            <div class="col-6">
                <h6>Victims Lost</h6>
                <p class="h4 text-danger">${state.lost_victims}/4</p>
            </div>
        </div>
        <div class="row">
            <div class="col-6">
                <h6>Structural Damage</h6>
                <p class="h4 text-warning">${state.damage_count}/24</p>
            </div>
            <div class="col-6">
                <h6>Rounds Played</h6>
                <p class="h4 text-info">${state.round_count}</p>
            </div>
        </div>
    `;

  modal.show();
}

// Funciones auxiliares
function translatePhase(phase) {
  const phases = {
    AGENT_TURN: "Agent Turn",
    FIRE_SPREAD: "Fire Spread",
  };
  return phases[phase] || phase;
}

function translateRole(role) {
  const roles = {
    RESCUER: "Rescuer",
    EXTINGUISHER: "Extinguisher",
    null: "No Role",
  };
  return roles[role] || role;
}
