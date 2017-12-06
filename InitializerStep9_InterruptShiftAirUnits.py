from CommandBuilder import CommandBuilder
from Constant import Constant
from Action import Action


class InitializerStep9_InterruptShiftAirUnits(CommandBuilder):
    def get_command_list(self):
        prepared_commands = []
        for vehicle_type in Constant.AIR_FORCE_TYPES:
            prepared_commands.append(Action.clear_and_select(vehicle_type=vehicle_type))
            prepared_commands.append(Action.move(0, Constant.CELL_SIZE / 2, 0.54))
        return prepared_commands
