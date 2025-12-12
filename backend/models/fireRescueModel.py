from mesa import Model
from mesa.space import MultiGrid

import numpy as np
import random

from models.fireAgent import FireAgent
from models.fireState import FireState
from models.firefighterRole import FireFighterRole
from models.poi import POI, POIType

wall_type = [0, 1, 2, 3, 4]  # 0: none, 1: wall 1hp, 2: wall 2hp, 3: open door
# 4: closed door

grid_layout = [
    [(2, 0, 2, 2), (2, 0, 2, 0), (2, 4, 2, 0), (2, 0, 0, 4), (2, 0, 0, 0), (2, 2, 0, 0), (2, 0, 0, 2), (2, 2, 0, 0)],
    [(2, 0, 0, 2), (2, 0, 0, 0), (2, 2, 0, 0), (0, 0, 2, 2), (0, 0, 2, 0), (0, 4, 4, 0), (0, 0, 0, 4), (0, 2, 0, 0)],
    [(0, 0, 0, 3), (0, 0, 2, 0), (0, 2, 0, 0), (2, 0, 0, 2), (2, 0, 0, 0), (4, 2, 0, 0), (0, 0, 0, 2), (0, 2, 0, 0)],
    [(0, 2, 4, 2), (2, 2, 0, 2), (0, 2, 0, 2), (0, 0, 2, 2), (0, 0, 0, 0), (0, 2, 0, 0), (0, 0, 2, 2), (0, 2, 2, 0)],
    [(4, 0, 0, 2), (0, 2, 0, 0), (0, 0, 2, 2), (2, 3, 2, 0), (0, 0, 4, 3), (0, 3, 2, 0), (2, 0, 0, 3), (2, 3, 0, 0)],
    [(0, 0, 2, 2), (0, 0, 2, 0), (2, 0, 2, 0), (2, 0, 2, 0), (4, 0, 2, 0), (2, 2, 2, 0), (0, 0, 2, 2), (0, 2, 2, 0)]
    ]

grid_data = np.array(grid_layout)

class FireRescueModel(Model):
    def __init__(self, grid_data):
        super().__init__()
        self.grid_data = grid_data
        height, width = grid_data.shape[:2]
        self.height = height
        self.width = width

        self.grid = MultiGrid(width, height, torus=False)
        self.running = True
        self.fire_states = np.full((height, width), FireState.CLEAR)
        self.step_count = 0
        self.damage_count = 0

        self.all_pois = []
        self.active_pois = []
        self.revealed_pois = []
        self.lost_victims = []
        self.rescued_victims = []
        self.pois_lost = []

        self.current_agent_index = 0
        self.agent_list = []
        self.round_count = 0
        self.phase = "AGENT_TURN"

        self.game_over = False
        self.game_won = False
        self.game_lost = False
        self.end_reason = ""

        self.stats = {
            "fire_count": [],
            "smoke_count": [],
            "clear_count": [],
            "damage_count": [],
            "rescued_victims": [],
            "lost_victims": [],
            "round": [],
        }

        self._create_poi_pool()
        self._place_initial_pois()
        self._place_initial_fires()
        self.place_firefighters()

    def _create_poi_pool(self):
        poi_id = 1
        for i in range(10):
            poi = POI(poi_id, POIType.VICTIM, -1, -1)
            self.all_pois.append(poi)
            poi_id += 1

        for i in range(5):
            poi = POI(poi_id, POIType.FALSE, -1, -1)
            self.all_pois.append(poi)
            poi_id += 1

        random.shuffle(self.all_pois)

    def _get_valid_positions_for_poi(self):
        valid_positions = []

        for y in range(self.height):
            for x in range(self.width):
                if any(poi.x == x and poi.y == y for poi in self.active_pois):
                    continue
                valid_positions.append((x, y))

        return valid_positions

    def _place_initial_pois(self):
        valid_positions = self._get_valid_positions_for_poi()

        if len(self.all_pois) == 0 or len(valid_positions) == 0:
            return

        num_pois = min(3, len(self.all_pois), len(valid_positions))
        initial_pois = random.sample(self.all_pois, num_pois)
        selected_positions = random.sample(valid_positions, num_pois)

        for poi, (x, y) in zip(initial_pois, selected_positions):
            poi.x = x
            poi.y = y
            self.active_pois.append(poi)

        for poi in initial_pois:
            self.all_pois.remove(poi)

    def _get_poi_at_position(self, x, y):
        for poi in self.active_pois:
            if poi.x == x and poi.y == y:
                return poi
        return None

    def place_new_poi(self):
        if len(self.all_pois) == 0:
            return None

        valid_positions = self._get_valid_positions_for_poi()
        if len(valid_positions) == 0:
            return None

        new_poi = random.choice(self.all_pois)
        selected_position = random.choice(valid_positions)

        new_poi.x = selected_position[0]
        new_poi.y = selected_position[1]
        self.fire_states[new_poi.y, new_poi.x] = FireState.CLEAR
        self.active_pois.append(new_poi)
        self.all_pois.remove(new_poi)

        self.assign_roles()

        return new_poi

    def reveal_poi(self, x, y):
        for poi in self.active_pois:
            if poi.x == x and poi.y == y and not poi.revealed:
                poi.revealed = True
                self.revealed_pois.append(poi)

                if poi.type == POIType.VICTIM:
                    print("Es una victima.")
                elif poi.type == POIType.FALSE:
                    print("Es una falsa alarma.")
                    self.active_pois.remove(poi)
                    self.place_new_poi()

                return True
        return False

    def rescue_victims(self, victim_poi):
        if victim_poi.type == POIType.VICTIM:
            self.rescued_victims.append(victim_poi)
            if victim_poi in self.active_pois:
                self.active_pois.remove(victim_poi)

            self.check_win_condition()
            self.assign_roles()

    def check_pois_in_danger(self):
        for poi in self.active_pois[:]:
            fire_state = self._get_fire_state(poi.x, poi.y)
            if fire_state == FireState.FIRE:
                if poi.type == POIType.VICTIM:
                    self.lost_victims.append(poi)
                self.active_pois.remove(poi)
                self.pois_lost.append(poi)
                self.place_new_poi()

        if len(self.lost_victims) >= 4:
            self.end_game(
                False, f"Derrota: {len(self.lost_victims)} victimas perdidas por fuego"
            )

        return self.pois_lost

    def _place_initial_fires(self):
        self.fire_states[1, 3] = FireState.FIRE
        self.fire_states[0, 7] = FireState.FIRE
        self.fire_states[3, 1] = FireState.FIRE

    def spread_fire_random(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)

        current_state = self._get_fire_state(x, y)

        if current_state == FireState.CLEAR:
            self._set_fire_state(x, y, FireState.SMOKE)

        elif current_state == FireState.SMOKE:
            self._set_fire_state(x, y, FireState.FIRE)

        elif current_state == FireState.FIRE:
            adjacent_cells = self._get_adjacent_cells(x, y)

            for adj in adjacent_cells:
                ax, ay = adj["pos"]
                wall_dir = adj["wall_dir"]

                can_pass = self.damage_wall(ax, ay, wall_dir)

                if can_pass:
                    adj_state = self._get_fire_state(ax, ay)

                    if adj_state == FireState.CLEAR:
                        self._set_fire_state(ax, ay, FireState.FIRE)
                    elif adj_state == FireState.SMOKE:
                        self._set_fire_state(ax, ay, FireState.FIRE)

    def spread_smoke_to_fire(self):
        fire_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self._get_fire_state(x, y) == FireState.FIRE:
                    fire_positions.append((x, y))

        smoke_to_convert = []
        for fx, fy in fire_positions:
            adjacent_cells = self._get_adjacent_cells(fx, fy)
            for adj in adjacent_cells:
                ax, ay = adj["pos"]
                wall_type = adj["wall_type"]
                if self._get_fire_state(ax, ay) == FireState.SMOKE and wall_type == 0:
                    smoke_to_convert.append((ax, ay))

        for sx, sy in smoke_to_convert:
            self._set_fire_state(sx, sy, FireState.FIRE)

    def _get_fire_state(self, x, y):
        return self.fire_states[y, x]

    def _set_fire_state(self, x, y, state):
        self.fire_states[y, x] = state

    def assign_roles(self):
        for agent in self.agent_list:
            agent.role = None
            agent.target_poi = None

        carrying_agents = []
        for agent in self.agent_list:
            if agent.carrying_victim:
                agent.role = FireFighterRole.RESCUER
                carrying_agents.append(agent)

        available_pois = []
        for poi in self.active_pois:
            if not poi.revealed:
                available_pois.append(poi)

        available_agents = []
        for agent in self.agent_list:
            if not agent.carrying_victim:
                available_agents.append(agent)

        potential_assignments = []
        for poi in available_pois:
            for agent in available_agents:
                distance = abs(poi.x - agent.pos[0]) + abs(poi.y - agent.pos[1])
                potential_assignments.append((distance, agent, poi))

        potential_assignments.sort(key=lambda x: x[0])
        assigned_rescuers = set(carrying_agents)
        poi_assignments = set()
        max_rescuers = 3

        for distance, agent, poi in potential_assignments:
            if len(assigned_rescuers) >= max_rescuers:
                break

            if agent not in assigned_rescuers and poi not in poi_assignments:
                agent.role = FireFighterRole.RESCUER
                agent.target_poi = poi
                assigned_rescuers.add(agent)
                poi_assignments.add(poi)

        for agent in self.agent_list:
            if agent.role is None and not agent.is_knocked_out():
                agent.role = FireFighterRole.EXTINGUISHER
                agent.target_poi = None

    def place_firefighters(self):
        valid_positions = []

        for y in range(self.height):
            for x in range(self.width):
                if self.fire_states[y, x] != FireState.CLEAR:
                    continue

                if any(poi.x == x and poi.y == y for poi in self.active_pois):
                    continue

                valid_positions.append((x, y))

        selected_positions = random.sample(valid_positions, 6)
        for i, pos in enumerate(selected_positions):
            firefighter = FireAgent(i, self)
            self.grid.place_agent(firefighter, pos)
            self.agent_list.append(firefighter)

        self.assign_roles()

    def get_current_agent(self):
        if not self.agent_list:
            return None
        return self.agent_list[self.current_agent_index]

    def agent_turn(self):
        current_agent = self.get_current_agent()
        if current_agent is None:
            self.phase = "FIRE_SPREAD"
            return

        print(
            f"\n-- Turno Agente {current_agent.unique_id} ({current_agent.role.value if current_agent.role else 'Sin Rol'}) ---"
        )
        current_agent.update_knockout()
        current_agent.reset_ap()

        if not current_agent.is_knocked_out():
            if current_agent.role == FireFighterRole.RESCUER:
                current_agent.rescuer_behavior()
            elif current_agent.role == FireFighterRole.EXTINGUISHER:
                current_agent.extinguisher_behavior()

        current_agent.check_knockout()
        self.current_agent_index = (self.current_agent_index + 1) % len(self.agent_list)
        self.phase = "FIRE_SPREAD"
        if self.current_agent_index == 0:
            self.round_count += 1

        self.step_count += 1

    def fire_spread_phase(self):
        print(f"\n-- FASE DE PROPAGACIÓN DEL FUEGO (Ronda {self.round_count}) ---")
        self.spread_fire_random()
        self.spread_smoke_to_fire()
        lost_pois = self.check_pois_in_danger()
        if lost_pois:
            victims_lost = sum(1 for p in lost_pois if p.type == POIType.VICTIM)
            alarms_destroyed = sum(1 for p in lost_pois if p.type == POIType.FALSE)
            print(
                f"¡{victims_lost} víctimas y {alarms_destroyed} falsas alarmas perdidas por fuego!"
            )
            self.assign_roles()
        self.step_count += 1
        self.phase = "AGENT_TURN"
        print(f"Contador de daño: {self.damage_count}")

    def _get_adjacent_cells(self, x, y):
        adjacent = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for i, (dx, dy) in enumerate(directions):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                wall_type, wall_dir = self._get_wall_between_cells(x, y, nx, ny)
                adjacent.append(
                    {
                        "pos": (nx, ny),
                        "wall_type": wall_type,
                        "wall_dir": wall_dir,
                        "source_pos": (x, y),
                    }
                )
        return adjacent

    def _get_wall_between_cells(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == -1:
            direction = 0
        elif dx == 1 and dy == 0:
            direction = 1
        elif dx == 0 and dy == 1:
            direction = 2
        elif dx == -1 and dy == 0:
            direction = 3
        else:
            return 0, -1

        if 0 <= x1 < self.width and 0 <= y1 < self.height:
            wall_type = self.grid_data[y1, x1, direction]
            return wall_type, direction
        else:
            return 0, -1

    def damage_wall(self, x, y, direction):
        if 0 <= x < self.width and 0 <= y < self.height:
            current_wall = self.grid_data[y, x, direction]
            if current_wall == 2:
                print(
                    f"Muro grueso dañado en ({x}, {y}), contador de daño: {self.damage_count}"
                )
                self.grid_data[y, x, direction] = 1
                self.damage_count += 1
                self.check_damage_loss_condition()
                return False
            elif current_wall == 1:
                print(
                    f"Muro destruido en ({x}, {y}), contador de daño: {self.damage_count}"
                )
                self.grid_data[y, x, direction] = 0
                self.damage_count += 1
                self.check_damage_loss_condition()
                return True
            elif current_wall in [3, 4]:
                self.grid_data[y, x, direction] = 0
                return True
            else:
                return True

    def check_damage_loss_condition(self):
        if self.damage_count > 24:
            self.end_game(False, "Derrota: Demasiados daños")

    def check_win_condition(self):
        if len(self.rescued_victims) >= 7:
            self.end_game(True, "Victoria: 7 victimas rescatadas")

    def end_game(self, won, reason):
        self.game_over = True
        self.game_won = won
        self.game_lost = not won
        self.end_reason = reason
        self.running = False

        print("JUEGO TERMINADO")
        print(f"{'=' * 50}")
        print(f"Resultado: {reason}")
        print("Estadísticas finales:")
        print(f"- Víctimas rescatadas: {len(self.rescued_victims)}/7")
        print(f"- Víctimas perdidas: {len(self.lost_victims)}/4")
        print(f"- Daño estructural: {self.damage_count}/24")
        print(f"- Rondas jugadas: {self.round_count}")

        fire_count = np.sum(self.fire_states == FireState.FIRE)
        smoke_count = np.sum(self.fire_states == FireState.SMOKE)
        clear_count = np.sum(self.fire_states == FireState.CLEAR)
        print(f"- Celdas de fuego: {fire_count}")
        print(f"- Celdas de humo: {smoke_count}")
        print(f"- Celdas limpias: {clear_count}")
        print(f"{'=' * 50}")

    def is_game_over(self):
        return self.game_over

    def get_agents_at_position(self, x, y):
        cell_contents = self.grid.get_cell_list_contents([(x, y)])
        return [agent for agent in cell_contents if isinstance(agent, FireAgent)]

    def count_agents_at_position(self, x, y):
        return len(self.get_agents_at_position(x, y))

    def get_all_agent_positions(self):
        positions = {}
        for agent in self.agent_list:
            if agent.pos:
                if agent.pos not in positions:
                    positions[agent.pos] = []
                positions[agent.pos].append(agent.unique_id)
        return positions

    def print_agent_distribution(self):
        positions = self.get_all_agent_positions()
        print("\n--- Distribución de Agentes ---")
        for pos, agent_ids in positions.items():
            if len(agent_ids) > 1:
                print(f"Posición {pos}: {len(agent_ids)} agentes - IDs: {agent_ids}")
        print("--- Fin Distribución ---\n")

    def step(self):
        if self.phase == "AGENT_TURN":
            self.agent_turn()
        elif self.phase == "FIRE_SPREAD":
            self.fire_spread_phase()

model = FireRescueModel(grid_data)

if __name__ == "__main__":
    while not model.is_game_over():
        model.step()