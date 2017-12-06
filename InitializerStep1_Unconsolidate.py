from CommandBuilder import CommandBuilder
from Formation import Formation
from Ownership import Ownership
from Constant import Constant
from Action import Action


class InitializerStep1_Unconsolidate(CommandBuilder):
    def get_command_list(self):
        types = Constant.MAX_SPEED
        sorted_types = [(k, types[k]) for k in sorted(types, key=types.get)]
        prepared_commands = []
        for vehicle_type, base_speed in sorted_types:
            f = Formation(self._all_vehicles, self._me, ownership=Ownership.ALLY, vehicle_type_list=[vehicle_type])
            topleft = f.find_topleft()
            bottomright = f.find_bottomright()
            path_from_topleft = (topleft[0] - Constant.UNIT_RADIUS, topleft[1] - Constant.UNIT_RADIUS)
            path_from_bottomright = (bottomright[0] + Constant.UNIT_RADIUS, bottomright[1] + Constant.UNIT_RADIUS)

            ytl = topleft[0]
            ybr = ytl + (Constant.INITIAL_FORMATION_UNITS_COUNT * 2 * Constant.UNIT_RADIUS +
                         (Constant.INITIAL_FORMATION_UNITS_COUNT - 1) * Constant.UNIT_INITIAL_DISTANCE)
            yc = (ytl + ybr) // 2
            max_distance = (ybr - ytl) * Constant.SANDWICH_UNCONSOLIDATE_FACTOR // 2
            path_to_topleft = (yc - max_distance - Constant.UNIT_RADIUS, path_from_topleft[1])
            path_to_bottomright = (yc + max_distance + Constant.UNIT_RADIUS, path_from_bottomright[1])

            for i in range(Constant.INITIAL_FORMATION_UNITS_COUNT):
                xtl = topleft[1] + i * (2 * Constant.UNIT_RADIUS + Constant.UNIT_INITIAL_DISTANCE)
                xbr = xtl + 2 * Constant.UNIT_RADIUS
                xc = xtl + Constant.UNIT_RADIUS
                if vehicle_type in Constant.GROUND_FORCE_TYPES:
                    speed_factor = self._terrain_map.get_minimum_speed_factor_on_path(path_from_topleft, path_from_bottomright, path_to_topleft, path_to_bottomright)
                else:
                    speed_factor = self._weather_map.get_minimum_speed_factor_on_path(path_from_topleft, path_from_bottomright, path_to_topleft, path_to_bottomright)
                prepared_commands.append(Action.clear_and_select((ytl, xtl), (ybr, xbr), vehicle_type))
                prepared_commands.append(Action.scale(xc, yc, Constant.SANDWICH_UNCONSOLIDATE_FACTOR, base_speed * speed_factor))
        return prepared_commands
