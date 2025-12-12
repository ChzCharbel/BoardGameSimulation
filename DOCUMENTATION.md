# 🔥 Multi-Agent Fire Rescue Simulation - Complete Documentation

A sophisticated **Multi-Agent System (MAS)** simulation built with Python, Flask, and the Mesa framework. This interactive web application demonstrates autonomous agent coordination, emergent behavior, and complex problem-solving based on the Fire Rescue board game.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Architecture Deep Dive](#-architecture-deep-dive)
3. [Server Architecture](#-server-architecture)
4. [Multi-Agent System](#-multi-agent-system)
5. [Game Mechanics](#-game-mechanics)
6. [API Reference](#-api-reference)
7. [WebSocket Events](#-websocket-events)
8. [Frontend Architecture](#-frontend-architecture)
9. [Installation & Setup](#-installation--setup)
10. [GitHub Pages Deployment](#-github-pages-deployment)
11. [Alternative Deployment Options](#-alternative-deployment-options)
12. [Configuration](#-configuration)
13. [Troubleshooting](#-troubleshooting)

---

## 🎯 Project Overview

### What is this project?

This is a web-based simulation of the **Fire Rescue** board game, implemented as a Multi-Agent System where 6 autonomous firefighter agents coordinate to rescue victims from a burning building.

### Key Features

| Feature | Description |
|---------|-------------|
| **Real-time Simulation** | Live updates via WebSockets |
| **Autonomous Agents** | 6 AI firefighters with individual decision-making |
| **Dynamic Role Assignment** | Agents switch between Rescuer and Extinguisher roles |
| **Pathfinding** | Dijkstra algorithm for optimal navigation |
| **Session Management** | Multiple concurrent simulations supported |
| **Interactive UI** | Step-by-step or automatic simulation modes |

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.8+, Flask 3.0.0, Flask-SocketIO 5.3.6 |
| **Agent Framework** | Mesa 3.0.3 (Agent-Based Modeling) |
| **Frontend** | Bootstrap 5.1.3, Socket.IO 4.5.0, Vanilla JavaScript |
| **Data Processing** | NumPy 2.3 |

---

## 🏗 Architecture Deep Dive

### Project Structure

```
BoardGameSimulation/
├── backend/                    # Python Flask backend
│   ├── __init__.py
│   ├── app.py                  # Flask application & WebSocket server
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── logs/                   # Application logs
│   └── models/                 # Mesa agent-based models
│       ├── __init__.py
│       ├── fireAgent.py        # FireAgent class (autonomous agent)
│       ├── firefighterRole.py  # Role enumeration
│       ├── fireRescueModel.py  # Mesa Model (environment)
│       ├── fireState.py        # Fire state enumeration
│       └── poi.py              # Points of Interest (victims)
│
├── frontend/                   # Static frontend assets
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Application styling
│   │   └── js/
│   │       ├── main.js         # Main JavaScript utilities
│   │       └── simulation.js   # Simulation controller & WebSocket client
│   └── templates/
│       ├── index.html          # Landing page
│       └── simulation.html     # Main simulation view
│
├── setup.py                    # Setup script
├── run.bat                     # Windows launcher
├── run.sh                      # Unix launcher
├── README.md                   # Original README
└── DOCUMENTATION.md            # This file
```

### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          BROWSER                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   index.html    │───▶│         simulation.html             │ │
│  └─────────────────┘    │  ┌─────────────────────────────────┐│ │
│                         │  │        simulation.js            ││ │
│                         │  │   - WebSocket Client            ││ │
│                         │  │   - UI Updates                  ││ │
│                         │  │   - API Calls                   ││ │
│                         │  └───────────┬─────────────────────┘│ │
│                         └──────────────┼──────────────────────┘ │
└────────────────────────────────────────┼────────────────────────┘
                                         │
                    HTTP/WebSocket       │
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FLASK SERVER                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                        app.py                                ││
│  │  ┌─────────────────┐   ┌─────────────────────────────────┐  ││
│  │  │  Flask Routes   │   │     Flask-SocketIO Events       │  ││
│  │  │  - /            │   │     - join_simulation           │  ││
│  │  │  - /simulation  │   │     - simulation_update         │  ││
│  │  │  - /api/*       │   │     - auto_status               │  ││
│  │  └────────┬────────┘   └──────────────┬──────────────────┘  ││
│  │           │                            │                     ││
│  │           └────────────┬───────────────┘                     ││
│  │                        ▼                                     ││
│  │           ┌────────────────────────┐                         ││
│  │           │   SimulationManager    │                         ││
│  │           │   - get_state()        │                         ││
│  │           │   - step()             │                         ││
│  │           │   - start_auto()       │                         ││
│  │           └───────────┬────────────┘                         ││
│  └───────────────────────┼──────────────────────────────────────┘│
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    MESA FRAMEWORK                            ││
│  │  ┌─────────────────────────────────────────────────────────┐││
│  │  │              FireRescueModel (Model)                    │││
│  │  │  - MultiGrid (8x6 spatial environment)                  │││
│  │  │  - Fire states matrix                                   │││
│  │  │  - POI management                                       │││
│  │  │  - Game logic & win/loss conditions                     │││
│  │  └───────────────────────┬─────────────────────────────────┘││
│  │                          ▼                                   ││
│  │  ┌─────────────────────────────────────────────────────────┐││
│  │  │               FireAgent (Agent) x6                      │││
│  │  │  - Dijkstra pathfinding                                 │││
│  │  │  - Role-based behavior (Rescuer/Extinguisher)           │││
│  │  │  - Action point management                              │││
│  │  │  - Victim carrying logic                                │││
│  │  └─────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 🖥 Server Architecture

### Flask Application (`app.py`)

The server is built with Flask and Flask-SocketIO, providing both REST API endpoints and real-time WebSocket communication.

#### Initialization

```python
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fire-rescue-secret-key-2025'
socketio = SocketIO(app, cors_allowed_origins="*")
```

#### SimulationManager Class

Each simulation session is managed by a `SimulationManager` instance:

```python
class SimulationManager:
    def __init__(self, simulation_id):
        self.simulation_id = simulation_id
        self.model = FireRescueModel(grid_data.copy())  # Mesa model
        self.is_running = False
        self.auto_step = False
        self.step_delay = 1  # seconds between automatic steps
```

**Key Methods:**

| Method | Description |
|--------|-------------|
| `get_state()` | Returns complete simulation state as JSON |
| `step()` | Executes one simulation step |
| `start_auto_simulation()` | Starts background thread for automatic stepping |
| `stop_auto_simulation()` | Stops automatic simulation |

#### State Serialization

The `get_state()` method serializes:
- Agent positions, roles, action points, knockout status
- POI locations and types (revealed/hidden)
- Fire states for each cell (CLEAR/SMOKE/FIRE)
- Grid data (walls, doors)
- Game statistics (rescued, lost, damage)

### Request Flow

1. **Client Request** → Flask route handler
2. **Route Handler** → Retrieves `SimulationManager` from `active_simulations` dict
3. **SimulationManager** → Calls Mesa model methods
4. **Mesa Model** → Updates agent/environment state
5. **Response** → JSON state sent back to client

### Threading Model

For automatic simulations:
```python
def start_auto_simulation(self):
    def auto_run():
        while self.auto_step and not self.model.is_game_over():
            self.step()
            socketio.emit('simulation_update', self.get_state(), room=self.simulation_id)
            time.sleep(self.step_delay)
    
    thread = threading.Thread(target=auto_run)
    thread.daemon = True  # Dies with main thread
    thread.start()
```

---

## 🤖 Multi-Agent System

### Agent Architecture (`fireAgent.py`)

Each `FireAgent` is an autonomous agent with:

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `action_points` | int | 4 points per turn for actions |
| `role` | FireFighterRole | RESCUER or EXTINGUISHER |
| `target_poi` | POI | Current rescue target |
| `carrying_victim` | POI | Victim being carried |
| `knockout_timer` | int | Turns until respawn (if knocked out) |
| `path` | list | Current navigation path |

#### Behavior State Machine

```
                    ┌──────────────────────────┐
                    │      Agent Step          │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   Reset Action Points    │
                    │        (4 AP)            │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
              No    │    Is Knocked Out?       │ Yes
          ┌─────────┤                          ├──────────┐
          │         └──────────────────────────┘          │
          │                                               │
          ▼                                               ▼
┌─────────────────────┐                      ┌────────────────────┐
│   Check Role        │                      │  Update Knockout   │
└─────────┬───────────┘                      │  Timer & Respawn   │
          │                                  └────────────────────┘
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌────────┐  ┌─────────────┐
│RESCUER │  │EXTINGUISHER │
└───┬────┘  └──────┬──────┘
    │              │
    ▼              ▼
┌──────────────┐  ┌──────────────┐
│rescuer_      │  │extinguisher_ │
│behavior()    │  │behavior()    │
└──────────────┘  └──────────────┘
```

#### Rescuer Behavior

1. **If carrying victim**: Navigate to nearest exit and rescue
2. **If has target POI**: Navigate to POI, reveal, and pick up if victim
3. **Else**: Find and extinguish nearest fire

#### Extinguisher Behavior

1. Find nearest fire/smoke cell
2. Navigate to target
3. Extinguish (2 AP for fire→clear, 1 AP for smoke→clear)

### Pathfinding (Dijkstra Algorithm)

```python
def djikstra(self, start, goal):
    g_score = {start: 0}
    open_set = [(g_score[start], start)]
    came_from = {}
    
    while open_set:
        current_distance, current = heapq.heappop(open_set)
        
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        for neighbor in self.get_neighbors(current):
            cost = self.get_move_cost(current, neighbor)
            tentative_g = g_score[current] + cost
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                heapq.heappush(open_set, (tentative_g, neighbor))
    
    return []  # No path found
```

### Movement Costs

| Obstacle | Cost |
|----------|------|
| Open cell | 1 AP |
| Open door | 1 AP |
| Closed door | 2 AP (opens it) |
| Wall | Cannot pass |

### Role Assignment Algorithm

```python
def assign_roles(self):
    # 1. Agents carrying victims → RESCUER
    # 2. Calculate distances from all agents to all unrevealed POIs
    # 3. Assign closest agents to POIs (max 3 rescuers)
    # 4. Remaining agents → EXTINGUISHER
```

---

## 🎮 Game Mechanics

### Model Overview (`fireRescueModel.py`)

The `FireRescueModel` manages:
- **8x6 Grid** with walls and doors
- **Fire states** (CLEAR, SMOKE, FIRE)
- **6 Firefighter agents**
- **Points of Interest** (10 victims + 5 false alarms)

### Game Phases

```
┌────────────────┐     ┌────────────────────┐
│  AGENT_TURN    │────▶│   FIRE_SPREAD      │
│                │     │                    │
│ Current agent  │     │ Random fire spawn  │
│ takes actions  │     │ Smoke→Fire spread  │
│                │     │ Check POI danger   │
└───────┬────────┘     └─────────┬──────────┘
        │                        │
        └────────────────────────┘
        (cycles through all agents)
```

### Fire Spread Mechanics

1. **Random Fire Spawn**: Pick random cell
   - CLEAR → SMOKE
   - SMOKE → FIRE
   - FIRE → Spread to adjacent cells (damaging walls)

2. **Smoke Conversion**: All smoke adjacent to fire (no wall) → FIRE

3. **POI Danger Check**: Victims in fire cells are lost

### Win/Loss Conditions

| Condition | Result |
|-----------|--------|
| 7 victims rescued | **WIN** |
| 4 victims lost | **LOSE** |
| 24+ structural damage | **LOSE** |

### Wall/Door System

```python
grid_layout = [
    # Each cell: (top, right, bottom, left)
    # 0: none, 1: wall 1hp, 2: wall 2hp, 3: open door, 4: closed door
    [(2, 0, 2, 2), (2, 0, 2, 0), ...],
    ...
]
```

---

## 📡 API Reference

### REST Endpoints

#### `GET /`
Returns the landing page (`index.html`).

#### `GET /simulation`
Returns the simulation page (`simulation.html`).

#### `POST /api/create_simulation`
Creates a new simulation instance.

**Response:**
```json
{
  "simulation_id": "uuid-string",
  "state": { /* full simulation state */ }
}
```

#### `GET /api/simulation/<id>/state`
Gets current state of a simulation.

**Response:**
```json
{
  "step_count": 0,
  "round_count": 0,
  "phase": "AGENT_TURN",
  "current_agent_index": 0,
  "fire_states": [[0,1,2,...], ...],
  "grid_data": [...],
  "agents": [...],
  "pois": [...],
  "rescued_victims": 0,
  "lost_victims": 0,
  "damage_count": 0,
  "game_over": false,
  "game_won": false,
  "stats": {
    "fire_count": 3,
    "smoke_count": 0,
    "clear_count": 45
  }
}
```

#### `POST /api/simulation/<id>/step`
Executes one simulation step.

#### `POST /api/simulation/<id>/auto_start`
Starts automatic simulation.

#### `POST /api/simulation/<id>/auto_stop`
Stops automatic simulation.

#### `DELETE /api/simulation/<id>/delete`
Deletes a simulation.

---

## 🔌 WebSocket Events

### Client → Server

| Event | Data | Description |
|-------|------|-------------|
| `join_simulation` | `{simulation_id: string}` | Join a simulation room |

### Server → Client

| Event | Data | Description |
|-------|------|-------------|
| `joined_simulation` | `{simulation_id: string}` | Confirmation of joining |
| `simulation_update` | Full state object | State update (after each step) |
| `auto_status` | `{auto_running: boolean}` | Auto-simulation status change |
| `error` | `{message: string}` | Error notification |

---

## 🎨 Frontend Architecture

### `simulation.js` Structure

```javascript
// Global State
let simulationId = null;
let socket = null;
let currentState = null;
let autoRunning = false;

// Initialization
document.addEventListener("DOMContentLoaded", function() {
    initializeSimulation();
    setupEventListeners();
});

// Key Functions
function initializeSocket()        // WebSocket setup
function createNewSimulation()     // POST /api/create_simulation
function loadSimulation(id)        // GET /api/simulation/:id/state
function stepSimulation()          // POST /api/simulation/:id/step
function toggleAutoSimulation()    // Toggle auto mode
function updateDisplay(state)      // Render state to UI
function updateGameBoard(state)    // Render grid
function createCell(x, y, state)   // Create cell element
```

### Grid Rendering

The 8x6 grid is rendered using CSS Grid:

```css
.game-board {
    display: grid;
    grid-template-columns: repeat(8, 60px);
    grid-template-rows: repeat(6, 60px);
    gap: 2px;
}
```

Each cell shows:
- Fire state (background color)
- Walls (CSS pseudo-elements)
- Agents (colored circles with role indicators)
- POIs (icons for victims/false alarms)

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.8+** (tested with 3.11)
- **pip** (Python package manager)

### Quick Start

#### Windows
```batch
# Clone the repository
git clone <repository-url>
cd BoardGameSimulation

# Run the launcher
run.bat
```

#### Linux/macOS
```bash
# Clone the repository
git clone <repository-url>
cd BoardGameSimulation

# Make launcher executable
chmod +x run.sh

# Run the launcher
./run.sh
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

### Access the Application

Open `http://localhost:5000` in your browser.

## ☁️ Alternative Deployment Options

### Option 1: Render (Recommended - Free Tier Available)

1. Create a `render.yaml`:
```yaml
services:
  - type: web
    name: fire-rescue-simulation
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --worker-class eventlet -w 1 app:app
```

2. Push to GitHub and connect Render

3. Add to `requirements.txt`:
```
gunicorn
eventlet
```

### Option 2: Railway (Free Tier Available)

1. Create a `Procfile`:
```
web: gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT
```

2. Push to GitHub and connect Railway

### Option 3: Heroku (Paid)

1. Create `Procfile`:
```
web: gunicorn --worker-class eventlet -w 1 app:app
```

2. Create `runtime.txt`:
```
python-3.11.4
```

3. Deploy:
```bash
heroku create fire-rescue-simulation
git push heroku main
```

### Option 4: Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn eventlet

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
```

Deploy to:
- **Google Cloud Run** (free tier)
- **AWS App Runner**
- **Azure Container Apps**
- **DigitalOcean App Platform**

### Option 5: VPS (Most Control)

1. Rent a VPS (DigitalOcean, Linode, Vultr - ~$5/month)
2. Install Python and dependencies
3. Use **nginx** as reverse proxy + **systemd** for process management

```nginx
# /etc/nginx/sites-available/fire-rescue
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## ⚙️ Configuration

### Environment Variables (`config.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `fire-rescue-secret-key-2025` | Flask session secret |
| `FLASK_DEBUG` | `True` | Debug mode |
| `FLASK_HOST` | `0.0.0.0` | Server host |
| `FLASK_PORT` | `5000` | Server port |
| `MAX_SIMULATIONS` | `100` | Max concurrent simulations |
| `DEFAULT_STEP_DELAY` | `2.0` | Auto-step delay (seconds) |
| `VICTIMS_TO_WIN` | `7` | Victims needed to win |
| `MAX_VICTIMS_LOST` | `4` | Max victims before losing |
| `MAX_STRUCTURAL_DAMAGE` | `24` | Max damage before collapse |

### Using .env File

Create a `.env` file:
```env
SECRET_KEY=your-production-secret-key
FLASK_DEBUG=False
FLASK_PORT=8080
DEFAULT_STEP_DELAY=1.0
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'mesa'"
```bash
pip install -r requirements.txt
```

#### 2. WebSocket connection fails
- Check that Flask-SocketIO is installed
- Ensure CORS is configured correctly
- Try a different browser

#### 3. Simulation not updating
- Check browser console for errors
- Verify WebSocket connection in Network tab
- Check server logs

#### 4. Port already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Additional Resources

- [Mesa Documentation](https://mesa.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Fire Rescue Board Game Rules](https://boardgamegeek.com/boardgame/76534/flash-point-fire-rescue)

---

*Documentation last updated: December 2025*
