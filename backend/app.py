from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import json
import sys
import os
import threading
import time
import numpy as np

# Importar los modelos
from models.fireRescueModel import FireRescueModel, grid_data
from models.fireState import FireState
from models.firefighterRole import FireFighterRole  
from models.poi import POIType

# Configure Flask with frontend paths
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
app = Flask(__name__, 
            template_folder=os.path.join(frontend_path, 'templates'),
            static_folder=os.path.join(frontend_path, 'static'))
app.config['SECRET_KEY'] = 'fire-rescue-secret-key-2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Almacenar las simulaciones activas
active_simulations = {}

class SimulationManager:
    def __init__(self, simulation_id):
        self.simulation_id = simulation_id
        self.model = FireRescueModel(grid_data.copy())
        self.is_running = False
        self.auto_step = False
        self.step_delay = 1  # segundos entre pasos automáticos
        
    def get_state(self):
        """Obtener el estado completo de la simulación"""
        agent_data = []
        for agent in self.model.agent_list:
            agent_info = {
                'id': agent.unique_id,
                'pos': agent.pos,
                'role': agent.role.value if agent.role else None,
                'action_points': agent.action_points,
                'carrying_victim': agent.carrying_victim.id if agent.carrying_victim else None,
                'knockout_timer': agent.knockout_timer,
                'is_knocked_out': agent.is_knocked_out()
            }
            agent_data.append(agent_info)
            
        poi_data = []
        for poi in self.model.active_pois:
            poi_info = {
                'id': poi.id,
                'x': poi.x,
                'y': poi.y,
                'type': poi.type.value,
                'revealed': poi.revealed
            }
            poi_data.append(poi_info)
            
        # Convertir fire_states a formato serializable
        fire_states_serializable = []
        for row in self.model.fire_states:
            row_data = []
            for cell in row:
                if cell == FireState.CLEAR:
                    row_data.append(0)
                elif cell == FireState.SMOKE:
                    row_data.append(1)
                elif cell == FireState.FIRE:
                    row_data.append(2)
                else:
                    row_data.append(0)  # default
            fire_states_serializable.append(row_data)
        
        return {
            'step_count': self.model.step_count,
            'round_count': self.model.round_count,
            'phase': self.model.phase,
            'current_agent_index': self.model.current_agent_index,
            'fire_states': fire_states_serializable,
            'grid_data': self.model.grid_data.tolist(),
            'agents': agent_data,
            'pois': poi_data,
            'rescued_victims': len(self.model.rescued_victims),
            'lost_victims': len(self.model.lost_victims),
            'damage_count': self.model.damage_count,
            'game_over': self.model.game_over,
            'game_won': self.model.game_won,
            'end_reason': self.model.end_reason if hasattr(self.model, 'end_reason') else '',
            'stats': {
                'fire_count': int(np.sum(self.model.fire_states == FireState.FIRE)),
                'smoke_count': int(np.sum(self.model.fire_states == FireState.SMOKE)),
                'clear_count': int(np.sum(self.model.fire_states == FireState.CLEAR))
            }
        }
    
    def step(self):
        """Ejecutar un paso de la simulación"""
        if not self.model.is_game_over():
            self.model.step()
            return True
        return False
    
    def start_auto_simulation(self):
        """Iniciar simulación automática en hilo separado"""
        if self.auto_step:  # Already running
            return
            
        self.auto_step = True
        
        # Emit auto status change
        socketio.emit('auto_status', {'auto_running': True}, room=self.simulation_id)
        
        def auto_run():
            while self.auto_step and not self.model.is_game_over():
                self.step()
                # Emitir estado actualizado a todos los clientes
                socketio.emit('simulation_update', self.get_state(), room=self.simulation_id)
                time.sleep(self.step_delay)
            
            # Auto-step finished (either stopped or game over)
            if not self.model.is_game_over():
                self.auto_step = False
            socketio.emit('auto_status', {'auto_running': False}, room=self.simulation_id)
        
        thread = threading.Thread(target=auto_run)
        thread.daemon = True
        thread.start()
    
    def stop_auto_simulation(self):
        """Detener simulación automática"""
        if not self.auto_step:  # Already stopped
            return
            
        self.auto_step = False
        
        # Emit auto status change
        socketio.emit('auto_status', {'auto_running': False}, room=self.simulation_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html')

@app.route('/api/create_simulation', methods=['POST'])
def create_simulation():
    """Crear una nueva simulación"""
    simulation_id = str(uuid.uuid4())
    sim_manager = SimulationManager(simulation_id)
    active_simulations[simulation_id] = sim_manager
    
    return jsonify({
        'simulation_id': simulation_id,
        'state': sim_manager.get_state()
    })

@app.route('/api/simulation/<simulation_id>/state')
def get_simulation_state(simulation_id):
    """Obtener el estado de una simulación"""
    if simulation_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404
    
    sim_manager = active_simulations[simulation_id]
    return jsonify(sim_manager.get_state())

@app.route('/api/simulation/<simulation_id>/step', methods=['POST'])
def step_simulation(simulation_id):
    """Ejecutar un paso manual de la simulación"""
    if simulation_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404
    
    sim_manager = active_simulations[simulation_id]
    success = sim_manager.step()
    
    return jsonify({
        'success': success,
        'state': sim_manager.get_state()
    })

@app.route('/api/simulation/<simulation_id>/auto_start', methods=['POST'])
def start_auto_simulation(simulation_id):
    """Iniciar simulación automática"""
    if simulation_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404
    
    sim_manager = active_simulations[simulation_id]
    sim_manager.start_auto_simulation()
    
    return jsonify({'success': True, 'message': 'Auto simulation started'})

@app.route('/api/simulation/<simulation_id>/auto_stop', methods=['POST'])
def stop_auto_simulation(simulation_id):
    """Detener simulación automática"""
    if simulation_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404
    
    sim_manager = active_simulations[simulation_id]
    sim_manager.stop_auto_simulation()
    
    return jsonify({'success': True, 'message': 'Auto simulation stopped'})

@app.route('/api/simulation/<simulation_id>/delete', methods=['DELETE'])
def delete_simulation(simulation_id):
    """Eliminar una simulación"""
    if simulation_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404
    
    sim_manager = active_simulations[simulation_id]
    sim_manager.stop_auto_simulation()
    del active_simulations[simulation_id]
    
    return jsonify({'success': True, 'message': 'Simulation deleted'})

# WebSocket events
@socketio.on('join_simulation')
def on_join_simulation(data):
    simulation_id = data['simulation_id']
    
    # Leave old room if exists
    old_simulation_id = session.get('simulation_id')
    if old_simulation_id and old_simulation_id != simulation_id:
        leave_room(old_simulation_id)
    
    if simulation_id in active_simulations:
        session['simulation_id'] = simulation_id
        join_room(simulation_id)
        sim_manager = active_simulations[simulation_id]
        
        # Send current state and auto status
        emit('joined_simulation', {'simulation_id': simulation_id})
        emit('simulation_update', sim_manager.get_state())
        emit('auto_status', {'auto_running': sim_manager.auto_step})
    else:
        emit('error', {'message': 'Simulation not found'})

@socketio.on('leave_simulation')
def on_leave_simulation(data):
    simulation_id = data.get('simulation_id')
    if simulation_id:
        leave_room(simulation_id)
        if session.get('simulation_id') == simulation_id:
            session.pop('simulation_id', None)

@socketio.on('disconnect')
def on_disconnect():
    simulation_id = session.get('simulation_id')
    if simulation_id:
        leave_room(simulation_id)
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)