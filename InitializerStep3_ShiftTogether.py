from CommandBuilder import CommandBuilder
from Constant import Constant
from Action import Action
from Formation import Formation
from Ownership import Ownership


class InitializerStep3_ShiftTogether(CommandBuilder):
    def get_command_list(self):
        prepared_commands = []
        for offset, column in {
            1: (Constant.CELL_DELIMITER_SIZE + Constant.CELL_TOTAL_SIZE * 0, Constant.CELL_TOTAL_SIZE * 1),
            -1: (Constant.CELL_DELIMITER_SIZE + Constant.CELL_TOTAL_SIZE * 2, Constant.CELL_TOTAL_SIZE * 3)
        }.items():
            f = Formation(self._all_vehicles, self._me, ownership=Ownership.ALLY, column=column)
            from_topleft, from_bottomright = f.find_topleft(), f.find_bottomright()
            to_topleft, to_bottomright = (from_topleft[0], from_topleft[1] + offset * Constant.CELL_TOTAL_SIZE), \
                                         (from_bottomright[0], from_bottomright[1] + offset * Constant.CELL_TOTAL_SIZE)
            speed_factor = self._terrain_map.get_minimum_speed_factor_on_path(from_topleft, from_bottomright, to_topleft, to_bottomright)
            prepared_commands.append(Action.clear_and_select(topleft=f.find_topleft(), bottomright=f.find_bottomright()))
            prepared_commands.append(Action.move(offset * Constant.CELL_TOTAL_SIZE, 0, 0.3 * speed_factor))
        return prepared_commands
