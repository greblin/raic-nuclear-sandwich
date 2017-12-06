from CommandBuilder import CommandBuilder
from Constant import Constant
from Action import Action


class InitializerStep3_ShiftTogether(CommandBuilder):
    def get_command_list(self):
        prepared_commands = []
        for offset, column in {
            1: (Constant.CELL_DELIMITER_SIZE + Constant.CELL_TOTAL_SIZE * 0, Constant.CELL_TOTAL_SIZE * 1),
            -1: (Constant.CELL_DELIMITER_SIZE + Constant.CELL_TOTAL_SIZE * 2, Constant.CELL_TOTAL_SIZE * 3)
        }.items():
            prepared_commands.append(Action.clear_and_select(topleft=(0, column[0]), bottomright=(Constant.WORLD_SIZE, column[1])))
            prepared_commands.append(Action.move(offset * Constant.CELL_TOTAL_SIZE, 0, 0.18))
        return prepared_commands
