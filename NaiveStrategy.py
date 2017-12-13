import math
import numpy as np
from model.World import World
from model.ActionType import ActionType

from Ownership import Ownership
from Formation import Formation
from ActionStrategy import ActionStrategy
from Action import Action
from ActionQueue import ActionQueue
from Constant import Constant
from WeatherMap import WeatherMap
from TerrainMap import TerrainMap


class NaiveStrategy(ActionStrategy):
    lastNuclearStrikeTick = 0
    nuclearStrikeInQueue = False
    currentOrthogonalVector = None

    def __init__(self, action_queue: ActionQueue, world: World, weather_map: WeatherMap, terrain_map: TerrainMap):
        super().__init__(action_queue, world, weather_map, terrain_map)
        self.lastNuclearStrikeTick = world.tick_index
        self.currentOrthogonalVector = np.array([0, 1])

    def determine_following_actions(self, updated_vehicle_x_y):
        if self.strategyTick < 0:
            pass
        elif self.strategyTick % 60 <= 5:
            ticks_from_nuclear_strike = self.world.tick_index - self.actionQueue.get_last_action_tick(ActionType.TACTICAL_NUCLEAR_STRIKE) if\
                self.actionQueue.get_last_action_tick(ActionType.TACTICAL_NUCLEAR_STRIKE) else self.world.tick_index
            if not self.actionQueue.is_action_in_queue(ActionType.TACTICAL_NUCLEAR_STRIKE) and\
                    (ticks_from_nuclear_strike > self.game.base_tactical_nuclear_strike_cooldown):
                points = self.calc_maximum_density_centers(self.allVehicles)
                if self.nuclear_strike(self.allVehicles, points):
                    return
            if len(updated_vehicle_x_y) > 0:
                return
            f = Formation(self.allVehicles, self.me, ownership=Ownership.ALLY)
            xc, yc = f.find_center()
            #target_x, target_y = (Formation(self.allVehicles, self.me, ownership=Ownership.ENEMY)).find_nearest(xc, yc)
            points = self.calc_maximum_density_centers(self.allVehicles)
            # primitive_mode = False
            target_x, target_y = None, None
            if len(points) > 0:
                pp_x, pp_y, target_count = points[0]
            #    if target_count <= 6 and len(points) > 15:
            #        primitive_mode = True
            #    else:
                enemies = Formation(self.allVehicles, self.me, ownership=Ownership.ENEMY, distance_limit=(pp_x, pp_y, 80))
                target_x, target_y = enemies.find_nearest(xc, yc)

            #if primitive_mode:
            #    if len(self.world.facilities) == 0:
            #        return
            #    else:
            #        target_y, target_x = None, None

            target_x = target_x - 10 if target_x is not None else None
            target_y = target_y - 10 if target_y is not None else None
            if (self.world.tick_index < 10000) and \
                    ((target_x is None) or (target_y is None) or ((target_x - xc) ** 2 + (target_y - yc) ** 2 >= 175 * 175)):
                for facility in self.world.facilities:
                    if facility.owner_player_id != self.me.id:
                        f_x, f_y = facility.left + 32, facility.top + 32
                        if not (96 <= f_x <= Constant.WORLD_SIZE - 96 and 96 <= f_y <= Constant.WORLD_SIZE - 96):
                            continue
                        if (target_x is None or target_y is None)\
                            or ((f_x - xc) ** 2 + (f_y - yc) ** 2 < (target_x - xc) ** 2 + (target_y - yc) ** 2):
                            target_x, target_y = f_x, f_y

            if target_x is None or target_y is None:
                return
            target_vector = np.array([target_x - xc, target_y - yc])

            angle = np.arccos(
                np.dot(self.currentOrthogonalVector, target_vector) /
                (np.linalg.norm(self.currentOrthogonalVector) * np.linalg.norm(target_vector))
            )
            det = self.currentOrthogonalVector[0] * target_vector[1] - self.currentOrthogonalVector[1] * target_vector[0]
            if det > 0:
                angle = -angle
            if abs(angle) > math.pi / 8:
                rot_angle = angle / 2
                #self.actionQueue.push(Action.clear_and_select())
                self.actionQueue.push(Action.rotate(xc, yc, -rot_angle, 0.18))
                rot_matrix = np.array([[np.cos(rot_angle), -np.sin(rot_angle)],
                                       [np.sin(rot_angle), np.cos(rot_angle)]])
                self.currentOrthogonalVector = np.dot(self.currentOrthogonalVector, rot_matrix)
            else:
                x_diff, y_diff = target_x - xc - 10, target_y - yc - 10
                if abs(x_diff) > 48:
                    x_diff = 48 if x_diff > 0 else -48
                if abs(y_diff) > 48:
                    y_diff = 48 if y_diff > 0 else -48

                from_topleft, from_bottomright = f.find_topleft(), f.find_bottomright()
                to_topleft = from_topleft[0] + y_diff, from_topleft[1] + x_diff
                to_bottomright = from_bottomright[0] + y_diff, from_bottomright[1] + x_diff
                speed_factor = self._terrain_map.get_minimum_speed_factor_on_path(from_topleft, from_bottomright, to_topleft, to_bottomright)

                #self.actionQueue.push(Action.clear_and_select())
                self.actionQueue.push(Action.move(x_diff, y_diff, 0.3 * speed_factor))


    def _find_maximum_density_squares(self, all_vehicles, x: int, y: int, size: int, min_size: int = 64):
        formation = Formation(all_vehicles, self.me, ownership=Ownership.ENEMY, square=(x, y, size))
        count = formation.get_count()
        if count == 0:
            return None
        if size <= min_size:
            return [(x, y, size, count)]
        size = size / 2
        subsquares = [
            (x, y, size),
            (x + size, y, size),
            (x, y + size, size),
            (x + size, y + size, size)
        ]
        result = []
        for (sx, sy, ssize) in subsquares:
            subresult = self._find_maximum_density_squares(all_vehicles, sx, sy, ssize, min_size)
            if subresult is not None:
                result = result + subresult
        return result

    def calc_maximum_density_centers(self, all_vehicles):
        maximum_density_squares = self._find_maximum_density_squares(all_vehicles, 0, 0, self.world.width)
        if maximum_density_squares is None:
            return []
        sorted_density = sorted(maximum_density_squares, key=lambda square: square[3], reverse=True)
        result = []
        for (sx, sy, ssize, count) in sorted_density:
            formation = Formation(all_vehicles, self.me, Ownership.ENEMY, square=(sx - ssize / 2, sy - ssize / 2, 2 * ssize))
            x, y = formation.find_powerpoint()
            if x is not None and y is not None:
                result.append((x, y, count))
        return result

    def nuclear_strike(self, all_vehicles, points):
        for x, y, count in points:
            ally_formation = Formation(all_vehicles, self.me, ownership=Ownership.ALLY, distance_limit=(x, y, 50))
            ally_estimated_damage = ally_formation.calc_nuclear_kill_factor(x, y)
            if ally_estimated_damage['killed'] + ally_estimated_damage['survived'] == 0:
                continue
            highlighter_id = ally_formation.find_nuclear_strike_highlighter(x, y, self.game, self.world)
            if highlighter_id is None:
                continue
            enemy_formation = Formation(all_vehicles, self.me, ownership=Ownership.ENEMY, distance_limit=(x, y, 50))
            enemy_estimated_damage = enemy_formation.calc_nuclear_kill_factor(x, y)
            enemy_checking = enemy_estimated_damage['killed'] > enemy_estimated_damage['survived'] or \
                             enemy_estimated_damage['total_damage'] >= 1000
            ally_checking = ally_estimated_damage['killed'] < ally_estimated_damage['survived'] / 5 and ally_estimated_damage['total_damage'] < 1000 or \
                            ally_estimated_damage['killed'] <= 5
            joint_checking = ally_estimated_damage['killed'] < enemy_estimated_damage['killed']
            if enemy_checking and joint_checking and ally_checking:
                self.actionQueue.push(Action.nuclear_strike(x, y, highlighter_id))
                return True
        return False




