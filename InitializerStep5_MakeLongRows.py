from CommandBuilder import CommandBuilder
from Constant import Constant
from Action import Action
from Formation import Formation
from Ownership import Ownership


class InitializerStep5_MakeLongRows(CommandBuilder):
    def get_command_list(self):
        group_height = Constant.SANDWICH_HORIZONTAL_GROUP_INDEX * (2 * Constant.UNIT_RADIUS + Constant.UNIT_INITIAL_DISTANCE)
        prepared_commands = []
        for group, offset in Constant.SANDWICH_GROUP_OFFSET.items():
            if offset == 0:
                continue
            f = Formation(self._all_vehicles, self._me, ownership=Ownership.ALLY, group_number=group)
            if f.get_count() == 0:
                continue
            from_topleft, from_bottomright = f.find_topleft(), f.find_bottomright()
            to_topleft, to_bottomright = (from_topleft[0] + offset * group_height, from_topleft[1]), \
                                         (from_bottomright[0] + offset * group_height, from_bottomright[1])
            speed_factor = self._terrain_map.get_minimum_speed_factor_on_path(from_topleft, from_bottomright, to_topleft, to_bottomright)
            prepared_commands.append(Action.clear_and_select(group=group))
            prepared_commands.append(Action.move(0, offset * group_height, 0.3 * speed_factor))
        return prepared_commands
