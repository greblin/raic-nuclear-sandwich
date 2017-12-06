from math import pi

from CommandBuilder import CommandBuilder
from Action import Action
from Formation import Formation
from Ownership import Ownership


class InitializerStep6_Rotate(CommandBuilder):
    def get_command_list(self):
        prepared_commands = []
        # f = Formation(self._all_vehicles, self._me, ownership=Ownership.ALLY)
        # yc, xc = f.find_geometrical_center()
        # prepared_commands.append(Action.clear_and_select())
        # prepared_commands.append(Action.rotate(xc, yc, -pi / 4, 0.18))
        prepared_commands.append(Action.clear_and_select())
        prepared_commands.append(Action.move(0, 1, 0.18))
        return prepared_commands
