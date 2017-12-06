from CommandBuilder import CommandBuilder
from Constant import Constant
from Action import Action


class InitializerStep2_ShiftVertical(CommandBuilder):
    def get_command_list(self):
        prepared_commands = []
        for offset, vehicle_types in Constant.SANDWICH_LINES.items():
            if offset != 0:
                for vehicle_type in vehicle_types:
                    y_offset = offset * (Constant.UNIT_RADIUS * 2 + Constant.UNIT_INITIAL_DISTANCE)
                    prepared_commands.append(Action.clear_and_select(vehicle_type=vehicle_type))
                    prepared_commands.append(Action.move(0, y_offset, 0.18))
        return prepared_commands
