# Multi-Agent Fire Rescue Simulation

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://fire-rescue-simulation.onrender.com/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)](https://flask.palletsprojects.com/)
[![Mesa](https://img.shields.io/badge/mesa-3.0-orange)](https://mesa.readthedocs.io/)

A sophisticated **Multi-Agent System (MAS)** implementation using Python and the Mesa framework. This interactive web application demonstrates autonomous agent coordination, emergent behavior, and complex problem-solving in a dynamic environment based on the Fire Rescue board game.

## 🌐 Live Demo

**[https://fire-rescue-simulation.onrender.com/](https://fire-rescue-simulation.onrender.com/)**

> Note: The free tier on Render may take ~30 seconds to wake up if the service has been idle.

## 🤖 System Overview

This simulation showcases key concepts in **Agent-Based Modeling (ABM)** and **Multi-Agent Systems**:

- **Autonomous Agents**: 6 firefighter agents with individual decision-making capabilities
- **Emergent Behavior**: Complex coordination patterns arise from simple interaction rules
- **Dynamic Role Assignment**: Agents adapt between Rescuer and Extinguisher roles
- **Intelligent Pathfinding**: Dijkstra algorithm for navigation through changing environments
- **Real-time Coordination**: Agents collaborate without centralized control
- **Interactive Web Interface**: Real-time visualization with Flask and WebSockets

## ✨ Features

### Real-time Simulation

- **Interactive Grid**: Live updates of agent positions and environment
- **Multi-Agent Tracking**: Individual agent status and role indicators
- **Environmental Dynamics**: Fire spread, smoke generation, structural damage
- **Manual & Automatic Control**: Step-by-step or continuous simulation modes
- **Performance Metrics**: Rescue statistics, coordination efficiency

### Advanced Agent Behaviors

- **Intelligent Navigation**: Dynamic pathfinding through changing environments
- **Role Adaptation**: Context-aware switching between rescue and firefighting
- **Resource Management**: Action point optimization and planning
- **Collision Avoidance**: Spatial coordination between multiple agents

### Web Application Features

- **WebSocket Communication**: Real-time multi-client synchronization
- **Session Management**: Multiple concurrent simulations
- **Responsive Design**: Works on desktop and mobile devices
- **Bootstrap UI**: Modern, professional interface

## 🏗️ Technical Architecture

### Core Components

```python
FireRescueModel (Mesa.Model)
├── MultiGrid Environment (8x6 spatial grid)
├── RandomActivation Scheduler
├── Agent Population (6 FirefighterAgents)
└── Environmental Systems (fire, walls, victims)
```

### Agent Intelligence Architecture

Each `FireAgent` implements:

- **State Machine**: Role-based behavior switching
- **Sensor Model**: Environmental perception and awareness
- **Decision Trees**: Action prioritization and planning
- **Pathfinding**: A\* algorithm for optimal navigation
- **Coordination**: Implicit communication through environment

## 🧠 Multi-Agent Implementation

### Agent Behavior Patterns

```python
class FireAgent(Agent):
    def __init__(self, unique_id, model):
        self.role = None                    # Dynamic role assignment
        self.action_points = 4             # Resource management
        self.carrying_victim = None        # State tracking
        self.knockout_timer = 0            # Agent health system

    def step(self):
        self.assign_role()                 # Dynamic role adaptation
        self.execute_behavior()            # Role-specific actions
        self.update_state()                # Internal state management
```

### Emergent Properties

The simulation demonstrates several emergent behaviors:

1. **Self-Organization**: Agents form rescue teams without central coordination
2. **Load Balancing**: Dynamic role distribution based on environmental needs
3. **Collective Intelligence**: Group problem-solving exceeds individual capabilities
4. **Adaptive Behavior**: System responds to changing fire patterns and victim locations

## 🔬 Simulation Parameters

| Parameter     | Value          | Description                    |
| ------------- | -------------- | ------------------------------ |
| Grid Size     | 8×6 cells      | Spatial environment dimensions |
| Agent Count   | 6 firefighters | Multi-agent population size    |
| Action Points | 4 per turn     | Resource constraint per agent  |
| Fire Spread   | Stochastic     | Dynamic environment changes    |
| Vision Range  | Adjacent cells | Agent sensory limitations      |
| Pathfinding   | Dijkstra       | Optimal route calculation      |

## 🛠️ Installation & Usage

### Requirements

```bash
Python 3.8+
Mesa 2.0+
Flask 3.0+
Flask-SocketIO 5.3+
NumPy 1.24+
python-dotenv 1.0+
```

### Quick Start

```bash
# Clone the repository
git clone [repository-url]
cd BoardGameSimulation

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment (creates .env file)
python setup.py

# Launch simulation
cd backend
python app.py
```

### Alternative Start Methods

```bash
# Windows
run.bat

# Linux/Mac
bash run.sh
```

### Development Setup

```bash
# Create development environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings

# Run application
cd backend
python app.py
```

## 🎮 How to Use

1. **Home Page**: Click "Launch Simulation" to create a new simulation
2. **Simulation Controls**:

   - **Step**: Execute one simulation step manually
   - **Auto**: Start/pause automatic continuous simulation
   - **Stop**: Stop automatic simulation
   - **Reset**: Create a new simulation

3. **Game Board Interpretation**:

   - **Light Brown**: Clean spaces
   - **Gray with dots**: Smoke
   - **Red/Orange animated**: Fire
   - **Blue circles**: Rescuer firefighters
   - **Red circles**: Extinguisher firefighters
   - **Pink squares**: Victims
   - **Orange squares**: False alarms

4. **Game Rules**:
   - **Objective**: Rescue 7 victims before losing 4 or taking >24 structural damage
   - **Agent Actions**: Each firefighter has 4 action points per turn
   - **Role Assignment**: Agents automatically become Rescuers or Extinguishers
   - **Fire Dynamics**: Fire spreads automatically each round
   - **Knockout System**: Agents in fire are unconscious for 2 turns

## 🌐 Web Application Structure

```
BoardGameSimulation/
├── backend/                    # Python Flask backend
│   ├── app.py                  # Flask application & WebSocket server
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── logs/                   # Application logs
│   └── models/                 # Mesa agent-based models
│       ├── fireRescueModel.py  # Main model class
│       ├── fireAgent.py        # Agent implementation
│       ├── fireState.py        # Environment states
│       ├── firefighterRole.py  # Agent roles
│       └── poi.py              # Points of interest
│
├── frontend/                   # Static frontend assets
│   ├── static/
│   │   ├── css/style.css       # Stylesheets
│   │   └── js/
│   │       ├── main.js         # Main page logic
│   │       └── simulation.js   # Simulation interface logic
│   └── templates/
│       ├── index.html          # Technical overview page
│       └── simulation.html     # Simulation interface
│
├── setup.py                    # Setup script
├── run.bat                     # Windows launcher
├── run.sh                      # Unix launcher
├── .env                        # Environment variables
└── DOCUMENTATION.md            # Detailed documentation
```

## 🔧 API Endpoints

- `POST /api/create_simulation` - Create new simulation
- `GET /api/simulation/<id>/state` - Get simulation state
- `POST /api/simulation/<id>/step` - Execute simulation step
- `POST /api/simulation/<id>/auto_start` - Start automatic mode
- `POST /api/simulation/<id>/auto_stop` - Stop automatic mode
- `DELETE /api/simulation/<id>/delete` - Delete simulation

## 🛡️ Configuration

The application uses environment variables for configuration:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# Simulation Parameters
MAX_SIMULATIONS=100
DEFAULT_STEP_DELAY=2.0
MAX_FIREFIGHTERS=6
VICTIMS_TO_WIN=7
```

## 📊 Core Knowledge

- **Multi-Agent Coordination**: Studying emergence in distributed systems
- **Crisis Management**: Modeling emergency response scenarios
- **Swarm Intelligence**: Collective problem-solving behaviors
- **Human-AI Interaction**: Mixed human-agent team dynamics
- **Algorithmic Game Theory**: Agent incentives and cooperation

## 🔍 Troubleshooting

### Common Issues

1. **Port 5000 in use**: Change `FLASK_PORT` in `.env`
2. **Dependencies missing**: Run `pip install -r requirements.txt`
3. **Permission errors**: Use virtual environment
4. **WebSocket errors**: Check firewall settings

### Development Tips

- Use `FLASK_DEBUG=True` for development
- Monitor console for agent behavior logs
- Use browser developer tools for WebSocket debugging

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Areas of interest:

- Advanced agent learning algorithms
- Alternative coordination mechanisms
- New environmental challenges
- Performance optimization
- Visualization enhancements
- Mobile responsiveness improvements