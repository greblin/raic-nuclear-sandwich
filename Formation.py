from model.Player import Player
from model.VehicleType import VehicleType
from model.Vehicle import Vehicle
from model.WeatherType import WeatherType
from model.TerrainType import TerrainType
from model.Game import Game
from model.World import World
from Ownership import Ownership
import math


class Formation:
    _formation = []

    def __init__(self,
                 all_vehicles: list,
                 me: Player,
                 ownership: Ownership = None,
                 vehicle_type_list=None,
                 group_number: int = None,
                 square: (int, int, int) = None,
                 distance_limit: (float, float, int) = None,
                 column:(int, int) = None,
                 out_of_column:(int, int) = None):
        criteria_seq = list([])
        if ownership:
            criteria_seq.append(
                (lambda vehicle: vehicle.player_id == me.id) if ownership == Ownership.ALLY else (lambda vehicle: vehicle.player_id != me.id)
            )
        if vehicle_type_list:
            criteria_seq.append(lambda vehicle: vehicle.type in vehicle_type_list)
        if group_number:
            criteria_seq.append(lambda vehicle: group_number in vehicle.groups)
        if square:
            x, y, size = square
            criteria_seq.append(lambda vehicle: x < vehicle.x <= x + size and y < vehicle.y <= y + size)
        if distance_limit:
            x, y, limit = distance_limit
            limit_sqr = limit ** 2
            criteria_seq.append(lambda vehicle: (x - vehicle.x) ** 2 + (y - vehicle.y) ** 2 <= limit_sqr)
        if column:
            x1, x2 = column
            criteria_seq.append(lambda vehicle: x1 <= round(vehicle.x, 5) <= x2)
        if out_of_column:
            x1, x2 = out_of_column
            criteria_seq.append(lambda vehicle: round(vehicle.x, 5) < x1 or round(vehicle.x, 5) > x2)
        self._formation = list(all_vehicles)
        for criteria in criteria_seq:
            self._formation = list(filter(criteria, self._formation))

    def get_count(self):
        return len(self._formation)



    def _find_mass_center(self, f):
        if len(self._formation) == 0:
            return None, None
        mass_sum = sum(map(f, self._formation))
        x = sum(map(lambda v: v.x * f(v), self._formation)) / mass_sum
        y = sum(map(lambda v: v.y * f(v), self._formation)) / mass_sum
        return round(x), round(y)

    def find_center(self):
        return self._find_mass_center(lambda vehicle: 1)

    def find_weakpoint(self):
        return self._find_mass_center(lambda vehicle: 1.0 / vehicle.durability)

    def find_powerpoint(self):
        return self._find_mass_center(lambda vehicle: vehicle.durability)



    def find_topleft(self):
        if self.get_count() == 0:
            return None, None
        return min(map(lambda v: v.y - v.radius, self._formation)), min(map(lambda v: v.x - v.radius, self._formation))

    def find_bottomright(self):
        if self.get_count() == 0:
            return None, None
        return max(map(lambda v: v.y + v.radius, self._formation)), max(map(lambda v: v.x + v.radius, self._formation))

    def find_geometrical_center(self):
        if self.get_count() == 0:
            return None, None
        ytl, xtl = self.find_topleft()
        ybr, xbr = self.find_bottomright()
        return (xtl + ybr) / 2, (xtl + xbr) / 2

    def check_all_vehicles_y_coords_in_list(self, y_list):
        return len([v for v in self._formation if round(v.y, 5) not in y_list]) == 0



    def get_average_durability(self):
        if len(self._formation) == 0:
            return None
        return sum(map(lambda v: v.durability, self._formation)) / len(self._formation)

    def find_nearest_ill(self, x, y):
        ill_formation = list(filter(lambda v: v.durability < 55, self._formation))
        if len(ill_formation) == 0:
            return None, None
        distance = list(map(lambda v: math.hypot(v.x - x, v.y - y), ill_formation))
        index = distance.index(min(distance))
        return ill_formation[index].x, ill_formation[index].y

    def find_nearest(self, x, y):
        if len(self._formation) == 0:
            return None, None
        distance = list(map(lambda v: math.hypot(v.x - x, v.y - y), self._formation))
        index = distance.index(min(distance))
        return self._formation[index].x, self._formation[index].y

    def calc_immobility_factor(self, updateTickList, current_tick, limit = 120):
        if len(self._formation) == 0:
            return None
        total = len(self._formation)
        immobile = len(list(filter(lambda v: current_tick - updateTickList[v.id] > limit, self._formation)))
        return 1.0 * immobile / total

    def calc_remaining_attack_factor(self):
        if len(self._formation) == 0:
            return None
        return 1.0 * sum(map(lambda v: v.remaining_attack_cooldown_ticks, self._formation)) / len(self._formation)

    def calc_durability_factor(self):
        if len(self._formation) == 0:
            return None
        return 1.0 * sum(map(lambda v: v.durability, self._formation)) / len(self._formation)

    def calc_nuclear_kill_factor(self, x, y):
        killed = 0
        survived = 0
        total_damage = 0
        for v in self._formation:
            distance = math.hypot(v.x - x, v.y - y)
            estimated_damage = 99 * (1 - distance * 0.02)
            estimated_damage = estimated_damage if estimated_damage > 0 else 0
            if v.durability > estimated_damage:
                survived = survived + 1
                total_damage = total_damage + estimated_damage
            else:
                killed = killed + 1
                total_damage = total_damage + v.durability
        return {'killed': killed, 'survived': survived, 'total_damage': total_damage}

    def find_nuclear_strike_highlighter(self, x, y, game: Game, world: World):
        if len(self._formation) == 0:
            return None

        def highlighter_criteria(x, y, v: Vehicle, game: Game, world: World):
            vision_range = v.vision_range
            i, j = math.floor(v.x / 32), math.floor(v.y / 32)
            if v.type in [VehicleType.FIGHTER, VehicleType.HELICOPTER]:
                weather_type = world.weather_by_cell_x_y[i][j]
                if weather_type == WeatherType.CLOUD:
                    vision_range = vision_range * game.cloud_weather_vision_factor
                elif weather_type == WeatherType.RAIN:
                    vision_range = vision_range * game.rain_weather_vision_factor
            else:
                terrain_type = world.terrain_by_cell_x_y[i][j]
                if terrain_type == TerrainType.FOREST:
                    vision_range = vision_range * game.forest_terrain_vision_factor
            return (v.x - x) ** 2 + (v.y - y) ** 2 <= vision_range ** 2

        potencial_highlighters = [v for v in self._formation if highlighter_criteria(x, y, v, game, world)]
        if len(potencial_highlighters) == 0:
            return None
        highlighter = max(potencial_highlighters, key=lambda v: v.durability)
        return highlighter.id
