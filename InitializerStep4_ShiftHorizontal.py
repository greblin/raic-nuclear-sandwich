from CommandBuilder import CommandBuilder
from Constant import Constant
from Formation import Formation
from Ownership import Ownership
from Action import Action


class InitializerStep4_ShiftHorizontal(CommandBuilder):
    def get_command_list(self):
        f = Formation(self._all_vehicles, self._me, ownership=Ownership.ALLY)
        base_y = f.find_topleft()[0]
        group_height = Constant.SANDWICH_HORIZONTAL_GROUP_INDEX * (2 * Constant.UNIT_RADIUS + Constant.UNIT_INITIAL_DISTANCE)
        central_column = (
            Constant.CELL_DELIMITER_SIZE + Constant.CELL_TOTAL_SIZE * 1,
            Constant.CELL_TOTAL_SIZE * 2
        )
        prepared_commands = []
        for i in range(Constant.SANDWICH_GROUP_COUNT):
            top_y = base_y + i * group_height
            bottom_y = base_y + (i + 1) * group_height
            offset = (Constant.CELL_SIZE + Constant.UNIT_INITIAL_DISTANCE) * (1 - i % Constant.SANDWICH_HORIZONTAL_GROUP_INDEX)
            base_speed = min(Constant.MAX_SPEED)
            speed_factor = self._terrain_map.get_minimum_speed_factor_on_path((top_y, central_column[0]),
                                                                              (bottom_y, central_column[1]),
                                                                              (top_y, central_column[0] + offset),
                                                                              (bottom_y, central_column[1] + offset))
            prepared_commands.append(Action.clear_and_select((top_y, central_column[0]), (bottom_y, central_column[1])))
            prepared_commands.append(Action.assign(i + 1))
            if offset == 0 or i == Constant.INITIAL_FORMATION_UNITS_COUNT - 1:
                continue
            prepared_commands.append(Action.move(offset, 0, base_speed * speed_factor))
        return prepared_commands
