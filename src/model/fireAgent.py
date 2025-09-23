from mesa import Agent
import numpy as np
import random
import heapq

from firefighterRole import FireFighterRole
from fireState import FireState
from poi import POIType

class FireAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.action_points = 4
        self.role = None
        self.target_poi = None
        self.carrying_victim = None
        self.knockout_timer = 0
        self.max_knockout_time = 2
        self.path = []
        self.unique_id = unique_id

    def reset_ap(self):
        self.action_points = 4

    def is_knocked_out(self):
        return self.knockout_timer > 0

    def update_knockout(self):
        if self.knockout_timer > 0:
            self.knockout_timer -= 1
            if self.knockout_timer == 0:
                self.action_points = 4
                self.respawn_agent()

    def respawn_agent(self):
        print(f"Agente {self.unique_id} respawneando desde {self.pos}")
        if self.carrying_victim:
            self.carrying_victim = None

        new_position = self.find_valid_respawn_position()
        if new_position:
            print(f"Agente {self.unique_id} respawneo en {new_position}")
            self.model.grid.move_agent(self, new_position)

        self.path = []

    def find_valid_respawn_position(self):
        valid_positions = []
        for y in range(self.model.height):
            for x in range(self.model.width):
                if self.model._get_fire_state(x, y) == FireState.CLEAR:
                    if not any(
                        poi.x == x and poi.y == y for poi in self.model.active_pois
                    ):
                        # Ya no verificamos si la celda está vacía porque ahora permitimos múltiples agentes
                        valid_positions.append((x, y))

        if valid_positions:
            return random.choice(valid_positions)

        return None

    def check_knockout(self):
        if self.pos and not self.is_knocked_out():
            fire_state = self.model._get_fire_state(self.pos[0], self.pos[1])
            if fire_state == FireState.FIRE:
                self.knockout_timer = self.max_knockout_time
                print(
                    f"Agente {self.unique_id} noqueado por fuego en la pocision {self.pos}!"
                )

    def rescuer_behavior(self):
        if self.carrying_victim:
            exits = [(0, 2), (7, 4)]
            target_exit = self.get_nearest_exit(exits)
            if target_exit is None:
                print(f"ERROR: Agente {self.unique_id} - No encuentra la salida LOL")
                return

            print(
                f"Agente {self.unique_id}: acarreando victima {self.carrying_victim.id}, posicion actual: {self.pos}, salida a la que va: {target_exit}"
            )

            if self.pos == target_exit:
                print(f"Victima salvada por FireFighter {self.unique_id}!")
                rescued_victim = self.carrying_victim
                self.carrying_victim = None
                self.model.rescue_victims(rescued_victim)
                return

            current_fire_state = self.model._get_fire_state(self.pos[0], self.pos[1])
            if current_fire_state == FireState.FIRE:
                self.extinguish_fire(self.pos[0], self.pos[1])
                return

            print(f"Agente {self.unique_id} moviendo a la salida: {target_exit}")
            self.move_with_fire_handling(target_exit)

        elif self.target_poi:
            if self.pos == (self.target_poi.x, self.target_poi.y):
                self.reveal_and_handle_poi()
                return

            current_fire_state = self.model._get_fire_state(self.pos[0], self.pos[1])
            if current_fire_state == FireState.FIRE:
                self.extinguish_fire(self.pos[0], self.pos[1])
                return

            print(
                f"Agente {self.unique_id}: Yendo al POI: ({self.target_poi.x}, {self.target_poi.y})"
            )
            self.move_with_fire_handling((self.target_poi.x, self.target_poi.y))

        else:
            nearby_fire = self.find_nearest_fire()
            if nearby_fire and self.action_points > 0:
                if self.pos == nearby_fire:
                    self.extinguish_fire(nearby_fire[0], nearby_fire[1])
                else:
                    self.move_towards_target(nearby_fire)

    def extinguisher_behavior(self):
        while self.action_points > 0:
            target = self.find_nearest_fire()
            if target:
                if self.pos == target:
                    self.extinguish_fire(target[0], target[1])
                else:
                    moved = self.move_towards_target(target)
                    if not moved:
                        break
            else:
                break

    def move_with_fire_handling(self, target):
        while self.action_points > 0:
            if self.pos == target:
                break

            current_fire_state = self.model._get_fire_state(self.pos[0], self.pos[1])
            if current_fire_state in [FireState.FIRE, FireState.SMOKE]:
                self.extinguish_fire(self.pos[0], self.pos[1])
                return
            moved = self.move_towards_target(target)
            if not moved:
                break

            new_fire_state = self.model._get_fire_state(self.pos[0], self.pos[1])
            if new_fire_state == FireState.FIRE:
                self.extinguish_fire(self.pos[0], self.pos[1])
                return

    def find_nearest_fire(self):
        best_target = None
        best_distance = float("inf")

        for y in range(self.model.height):
            for x in range(self.model.width):
                fire_state = self.model._get_fire_state(x, y)
                if fire_state in [FireState.FIRE, FireState.SMOKE]:
                    distance = abs(x - self.pos[0]) + abs(y - self.pos[1])
                    if distance < best_distance:
                        best_target = (x, y)
                        best_distance = distance

        return best_target

    def extinguish_fire(self, x, y):
        fire_state = self.model._get_fire_state(x, y)

        if fire_state == FireState.FIRE:
            if self.action_points >= 2:
                self.action_points -= 2
                self.model._set_fire_state(x, y, FireState.CLEAR)
            elif self.action_points >= 1:
                self.action_points -= 1
                self.model._set_fire_state(x, y, FireState.SMOKE)
        elif fire_state == FireState.SMOKE:
            if self.action_points >= 1:
                self.action_points -= 1
                self.model._set_fire_state(x, y, FireState.CLEAR)

    def get_nearest_exit(self, exits):
        best_exit = None
        best_distance = float("inf")

        for exit in exits:
            distance = abs(exit[0] - self.pos[0]) + abs(exit[1] - self.pos[1])
            if distance < best_distance:
                best_exit = exit
                best_distance = distance

        return best_exit

    def reveal_and_handle_poi(self):
        if self.action_points > 0:
            print(
                f"Agente {self.unique_id} encontro un POI en {self.target_poi.x}, {self.target_poi.y}"
            )
            reveal_success = self.model.reveal_poi(self.target_poi.x, self.target_poi.y)
            if reveal_success:
                if self.target_poi is not None:
                    if (
                        self.target_poi.type == POIType.VICTIM
                        and self.target_poi not in self.model.lost_victims
                    ):
                        self.carrying_victim = self.target_poi
                        print(
                            f"Agente {self.unique_id} acarreando {self.target_poi.id}"
                        )
                        if self.target_poi in self.model.active_pois:
                            self.model.active_pois.remove(self.target_poi)

                        new_poi = self.model.place_new_poi()
                        if new_poi:
                            print(f"Nuevo POI en {new_poi.x}, {new_poi.y})")

            self.target_poi = None
            self.action_points -= 1

    def move_towards_target(self, target):
        if self.action_points <= 0:
            return False

        if not self.path or (len(self.path) > 0 and self.path[-1] != target):
            print(f"Nuevo Path desde {self.pos} hasta {target}")
            self.path = self.djikstra(self.pos, target)
            print(f"Agente {self.unique_id} path: {self.path}")

        if self.path and len(self.path) > 1:
            next_pos = self.path[1]
            cost = self.get_move_cost(self.pos, next_pos)
            if self.action_points >= cost:
                wall_type, wall_dir = self.model._get_wall_between_cells(
                    self.pos[0], self.pos[1], next_pos[0], next_pos[1]
                )
                if wall_type == 0 or wall_type == 3:
                    self.model.grid.move_agent(self, next_pos)
                    self.action_points -= cost
                    self.path.pop(0)
                    if self.carrying_victim:
                        self.carrying_victim.x = self.pos[0]
                        self.carrying_victim.y = self.pos[1]
                        print(
                            f"Agente {self.unique_id}: se movio a {self.pos} con una victima"
                        )
                    return True
                elif wall_type == 4:
                    self.open_door(self.pos[0], self.pos[1], wall_dir)
                    self.path.pop(0)
                    return True
                else:
                    self.path = []
                    return False
            else:
                return False
        return False

    def get_move_cost(self, pos, next_pos):
        wall_type, _ = self.model._get_wall_between_cells(
            pos[0], pos[1], next_pos[0], next_pos[1]
        )
        if wall_type == 0 or wall_type == 3:
            return 1
        elif wall_type == 4:
            return 2
        else:
            return float("inf")

    def chop_wall(self, x, y, direction):
        if self.action_points >= 1:
            self.model.damage_wall(x, y, direction)
            self.action_points -= 1

    def open_door(self, x, y, direction):
        if (
            self.action_points >= 1
            and 0 <= x < self.model.width
            and 0 <= y < self.model.height
        ):
            if self.model.grid_data[y, x, direction] == 4:
                self.model.grid_data[y, x, direction] = 3
                self.action_points -= 1
                print(f"Agente {self.unique_id} abrio puerta ({x}, {y})")

    def djikstra(self, start, goal):
        if start == goal:
            return [start]

        g_score = {start: 0}
        open_set = [(g_score[start], start)]
        came_from = {}
        visited = set()

        while open_set:
            current_distance, current = heapq.heappop(open_set)

            if current in visited:
                continue

            visited.add(current)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor in visited:
                    continue

                tentative_g_score = g_score[current] + self.get_move_cost(
                    current, neighbor
                )

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heapq.heappush(open_set, (tentative_g_score, neighbor))

        return []

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = []
        directions = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
        ]  # arriba, derecha, abajo, izquierda

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                neighbors.append((nx, ny))

        return neighbors
    
    def step(self):
        self.reset_ap()
        self.update_knockout()

        if self.is_knocked_out():
            print(
                f"Agente {self.unique_id}: Esta noqueado mi pa, saltando su turno LOL"
            )
            return

        if self.role is None:
            if self.carrying_victim:
                self.role = FireFighterRole.RESCUER
            else:
                self.role = FireFighterRole.EXTINGUISHER

        if self.role == FireFighterRole.RESCUER:
            self.rescuer_behavior()
        elif self.role == FireFighterRole.EXTINGUISHER:
            self.extinguisher_behavior()

        self.check_knockout()