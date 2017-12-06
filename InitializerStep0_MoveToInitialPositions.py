import itertools
from functools import reduce

from model.Player import Player
from model.VehicleType import VehicleType

from CommandBuilder import CommandBuilder
from Constant import Constant
from Formation import Formation
from Ownership import Ownership
from WeatherMap import WeatherMap
from TerrainMap import TerrainMap
from Action import Action


class InitializerStep0_MoveToInitialPositions(CommandBuilder):
    __matrix = []
    __positions = {}

    __possible_configurations = [
        [{VehicleType.FIGHTER, VehicleType.IFV}, {VehicleType.TANK}, {VehicleType.HELICOPTER, VehicleType.ARRV}],
        [{VehicleType.FIGHTER, VehicleType.IFV}, {VehicleType.ARRV}, {VehicleType.HELICOPTER, VehicleType.TANK}],
        [{VehicleType.FIGHTER, VehicleType.TANK}, {VehicleType.IFV}, {VehicleType.HELICOPTER, VehicleType.ARRV}],
        [{VehicleType.FIGHTER, VehicleType.TANK}, {VehicleType.ARRV}, {VehicleType.HELICOPTER, VehicleType.IFV}],
        [{VehicleType.FIGHTER, VehicleType.ARRV}, {VehicleType.IFV}, {VehicleType.HELICOPTER, VehicleType.TANK}],
        [{VehicleType.FIGHTER, VehicleType.ARRV}, {VehicleType.TANK}, {VehicleType.HELICOPTER, VehicleType.IFV}]
    ]

    def __init__(self, me: Player, weather_map: WeatherMap, terrain_map: TerrainMap, all_vehicles):
        super().__init__(me, weather_map, terrain_map, all_vehicles)
        self.__matrix = []
        self.__positions = {}

        for i in range(Constant.INITIAL_MATRIX_ROWS_COUNT):
            self.__matrix.insert(i, [])
            for j in range(Constant.INITIAL_MATRIX_COLS_COUNT):
                self.__matrix[i].insert(j, set())
        for vehicle_type in Constant.ALL_FORCE_TYPES:
            f = Formation(all_vehicles, self._me, ownership=Ownership.ALLY, vehicle_type_list=[vehicle_type])
            tly, tlx = f.find_topleft()
            if tly is None or tlx is None:
                continue
            i = (round(tly) - Constant.CELL_DELIMITER_SIZE) // Constant.CELL_TOTAL_SIZE
            j = (round(tlx) - Constant.CELL_DELIMITER_SIZE) // Constant.CELL_TOTAL_SIZE
            self.__matrix[i][j] = self.__matrix[i][j] | {vehicle_type}
            self.__positions[vehicle_type] = (i, j)

    def __generate_optimal_position(self):
        positions = []
        for conf in self.__possible_configurations:
            permutations = list(itertools.permutations(conf))
            for permutation in permutations:
                potencial_position = dict()
                potencial_diff = dict()
                unreachable = False
                for vt in Constant.ALL_FORCE_TYPES:
                    for j in range(3):
                        if vt in permutation[j]:
                            set_in_pos = self.__matrix[Constant.INITIAL_ROW][j]
                            if vt in Constant.AIR_FORCE_TYPES:
                                critical_set = set(Constant.AIR_FORCE_TYPES) - {vt}
                            else:
                                critical_set = set(Constant.GROUND_FORCE_TYPES) - {vt}
                            if len(set_in_pos & critical_set) != 0:
                                unreachable = True
                                break
                            potencial_position[vt] = (Constant.INITIAL_ROW, j)
                    if unreachable:
                        break
                    potencial_diff[vt] = (potencial_position[vt][0] - self.__positions[vt][0],
                                          potencial_position[vt][1] - self.__positions[vt][1])
                if not unreachable:
                    potencial_duration = (
                        sum([sum(map(abs, diff)) * 2 for vt, diff in potencial_diff.items() if vt in Constant.GROUND_FORCE_TYPES]),
                        sum([sum(map(abs, diff)) for vt, diff in potencial_diff.items() if vt in Constant.AIR_FORCE_TYPES])
                    )
                    positions.append({'target': potencial_position, 'diff': potencial_diff, 'duration': potencial_duration})
        optimal = reduce(lambda x, y: x if min(x['duration'], y['duration']) == x['duration'] else y, positions)
        return optimal

    def __build_commands(self, optimal_position, force_list):
        optimal_position_list = []
        path_matrix = []
        commands = []
        for i in range(Constant.INITIAL_MATRIX_ROWS_COUNT):
            path_matrix.insert(i, [])
            for j in range(Constant.INITIAL_MATRIX_COLS_COUNT):
                path_matrix[i].insert(j, set())

        for f in force_list:
            optimal_position_list.insert(f, [f, optimal_position['target'][f], optimal_position['diff'][f], optimal_position['duration']])
            i, j = self.__positions[f]
            path_matrix[i][j] = path_matrix[i][j] | {f}

        sorted_optimal_position_list = sorted(optimal_position_list, key=lambda o: abs(o[2][0]) + abs(o[2][1]), reverse=True)
        for o in sorted_optimal_position_list:
            f = o[0]
            potencial_diff_list = [(o[2][0], 0), (0, o[2][1])]
            for i_diff, j_diff in potencial_diff_list:
                if i_diff == 0 and j_diff == 0:
                    continue
                i, j = self.__positions[f]
                new_i, new_j = i + i_diff, j + j_diff
                add_command = True
                test_i_range = range(min(i, new_i), max(i, new_i) + 1)
                test_j_range = range(min(j, new_j), max(j, new_j) + 1)
                for test_i in test_i_range:
                    for test_j in test_j_range:
                        if len(path_matrix[test_i][test_j] & (set(force_list) - {f})) != 0:
                            add_command = False
                if add_command:
                    for test_i in test_i_range:
                        for test_j in test_j_range:
                            path_matrix[test_i][test_j] = path_matrix[test_i][test_j] | {f}
                    commands.append({'type': f, 'diff': (i_diff, j_diff), 'current': self.__positions[f]})
                    break
        return commands

    def get_command_list(self):
        optimal_position = self.__generate_optimal_position()
        ground_force_commands = self.__build_commands(optimal_position, Constant.GROUND_FORCE_TYPES)
        air_force_commands = self.__build_commands(optimal_position, Constant.AIR_FORCE_TYPES)
        commands = ground_force_commands + air_force_commands
        prepared_commands = []
        for command in commands:
            if command is not None:
                topleft = [c * Constant.CELL_TOTAL_SIZE + Constant.CELL_DELIMITER_SIZE for c in command['current']]
                bottomright = [(c + 1) * Constant.CELL_TOTAL_SIZE for c in command['current']]
                diff = [d * Constant.CELL_TOTAL_SIZE for d in command['diff']]
                target_topleft = (topleft[0] + diff[0], topleft[1] + diff[1])
                target_bottomright = (bottomright[0] + diff[0], bottomright[1] + diff[1])

                base_speed = Constant.MAX_SPEED[command['type']]
                characteristic_map = self._weather_map if command['type'] in Constant.AIR_FORCE_TYPES else self._terrain_map
                speed_factor = characteristic_map.get_minimum_speed_factor_on_path(topleft, bottomright, target_topleft, target_bottomright)

                prepared_commands.append(Action.clear_and_select(topleft, bottomright, command['type']))
                prepared_commands.append(Action.move(diff[1], diff[0], base_speed * speed_factor))
        return prepared_commands
