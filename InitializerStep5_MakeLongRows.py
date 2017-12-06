from CommandBuilder import CommandBuilder
from Constant import Constant
from Action import Action


class InitializerStep5_MakeLongRows(CommandBuilder):
    def get_command_list(self):
        group_height = Constant.SANDWICH_HORIZONTAL_GROUP_INDEX * (2 * Constant.UNIT_RADIUS + Constant.UNIT_INITIAL_DISTANCE)
        prepared_commands = []
        for group, offset in Constant.SANDWICH_GROUP_OFFSET.items():
            if offset == 0:
                continue
            prepared_commands.append(Action.clear_and_select(group=group))
            prepared_commands.append(Action.move(0, offset * group_height, 0.18))
        return prepared_commands
