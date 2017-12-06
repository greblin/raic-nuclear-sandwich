from model.World import World
from model.Player import Player

from ActionQueue import ActionQueue
from CommandBuilder import CommandBuilder
from InitializerStep0_MoveToInitialPositions import InitializerStep0_MoveToInitialPositions
from InitializerStep1_Unconsolidate import InitializerStep1_Unconsolidate
from InitializerStep2_ShiftVertical import InitializerStep2_ShiftVertical
from InitializerStep3_ShiftTogether import InitializerStep3_ShiftTogether
from InitializerStep4_ShiftHorizontal import InitializerStep4_ShiftHorizontal
from InitializerStep5_MakeLongRows import InitializerStep5_MakeLongRows
from InitializerStep6_Rotate import InitializerStep6_Rotate
from InitializerStep8_InterruptConsolidate import InitializerStep8_InterruptConsolidate
from InitializerStep9_InterruptShiftAirUnits import InitializerStep9_InterruptShiftAirUnits
from WeatherMap import WeatherMap
from TerrainMap import TerrainMap
from Constant import Constant
from Formation import Formation
from Ownership import Ownership

class Initializer:
    STEP_MOVE_TO_INITIAL_POSITIONS = 0
    STEP_UNCONSOLIDATE = 1
    STEP_SHIFT_VERTICAL = 2
    STEP_SHIFT_TOGETHER = 3
    STEP_SHIFT_HORIZONTAL = 4
    STEP_MAKE_LONG_ROWS = 5
    STEP_ROTATE = 6
    STEP_STOP = 7
    STEP_INTERRUPT_CONSOLIDATE = 8
    STEP_INTERRUPT_SHIFT_AIR_UNITS = 9
    STEP_INTERRUPT_STOP = 10
    STEP_MAX = 100

    current_step = STEP_MOVE_TO_INITIAL_POSITIONS
    __step_started = []
    __step_move_started = []

    __me = None
    __all_vehicles = None
    __world = None

    __weather_map = None
    __terrain_map = None

    def __init__(self, world: World):
        self.__world = world
        for i in range(self.STEP_MAX + 1):
            self.__step_started.insert(i, False)
            self.__step_move_started.insert(i, False)
        self.__weather_map = WeatherMap(world.weather_by_cell_x_y, Constant.WEATHER_MAP_CELL_SIZE)
        self.__terrain_map = TerrainMap(world.terrain_by_cell_x_y, Constant.TERRAIN_MAP_CELL_SIZE)

    def prepare_step(self, me: Player, world: World, all_vehicles):
        self.__me = me
        self.__world = world
        self.__all_vehicles = all_vehicles

    def __set_step(self, new_step=None):
        new_step = self.current_step + 1 if new_step is None else new_step
        # print('Step %d => %d on tick: %d' % (self.current_step, new_step, self.__world.tick_index))
        self.current_step = new_step

    def __mark_step_started(self, status=True):
        self.__step_started[self.current_step] = status

    def __mark_move_started(self, status=True):
        self.__step_move_started[self.current_step] = status

    def __check_step_started(self):
        return self.__step_started[self.current_step]

    def __check_move_started(self):
        return self.__step_move_started[self.current_step]

    def __check_move_finished(self, updated_vehicle_x_y):
        if len(updated_vehicle_x_y) > 0:
            self.__mark_move_started()
        else:
            if self.__check_move_started():
                return True
        return False

    def __perform_casual_step(self, command_builder_class, action_queue: ActionQueue, updated_vehicle_x_y):
        if not self.__check_step_started():
            command_builder = command_builder_class(self.__me, self.__weather_map, self.__terrain_map, self.__all_vehicles)
            commands = command_builder.get_command_list()
            if len(commands) == 0:
                self.__set_step()
                return
            for command in commands:
                action_queue.push(command)
            self.__mark_step_started()
        elif self.__check_move_finished(updated_vehicle_x_y):
            self.__set_step()

    def perform_current_step(self, action_queue: ActionQueue, updated_vehicle_x_y):
        # Двигаем юниты на 1 линию
        if self.current_step == self.STEP_MOVE_TO_INITIAL_POSITIONS:
            if not self.__check_step_started():
                command_builder = InitializerStep0_MoveToInitialPositions(self.__me, self.__weather_map, self.__terrain_map, self.__all_vehicles)
                commands = command_builder.get_command_list()
                if len(commands) == 0:
                    if self.__check_interrupt_condition():
                        self.__set_step(self.STEP_INTERRUPT_CONSOLIDATE)
                    else:
                        self.__set_step()
                    return
                for command in commands:
                    action_queue.push(command)
                self.__mark_step_started()
            if self.__check_move_finished(updated_vehicle_x_y):
                self.__mark_move_started(False)
                self.__mark_step_started(False)
        # Расширяем каждый столбец юнитов в 3 раза
        elif self.current_step == self.STEP_UNCONSOLIDATE:
            self.__perform_casual_step(InitializerStep1_Unconsolidate, action_queue, updated_vehicle_x_y)
        # Делаем вертикальный сдвиг на разное смещение разных типов юнитов
        elif self.current_step == self.STEP_SHIFT_VERTICAL:
            self.__perform_casual_step(InitializerStep2_ShiftVertical, action_queue, updated_vehicle_x_y)
        # Сдвигаем юнитов в одну колонку
        elif self.current_step == self.STEP_SHIFT_TOGETHER:
            self.__perform_casual_step(InitializerStep3_ShiftTogether, action_queue, updated_vehicle_x_y)
        # Сдвигаем группы по 3 через 3
        elif self.current_step == self.STEP_SHIFT_HORIZONTAL:
            self.__perform_casual_step(InitializerStep4_ShiftHorizontal, action_queue, updated_vehicle_x_y)
        # Формируем длинные ряды
        elif self.current_step == self.STEP_MAKE_LONG_ROWS:
            self.__perform_casual_step(InitializerStep5_MakeLongRows, action_queue, updated_vehicle_x_y)
        # Поворачиваемся
        elif self.current_step == self.STEP_ROTATE:
            self.__perform_casual_step(InitializerStep6_Rotate, action_queue, updated_vehicle_x_y)
        elif self.current_step == self.STEP_INTERRUPT_CONSOLIDATE:
            self.__perform_casual_step(InitializerStep8_InterruptConsolidate, action_queue, updated_vehicle_x_y)
        elif self.current_step == self.STEP_INTERRUPT_SHIFT_AIR_UNITS:
            self.__perform_casual_step(InitializerStep9_InterruptShiftAirUnits, action_queue, updated_vehicle_x_y)

    def __check_interrupt_condition(self):
        return False  # кажется, прерывание построения было ошибочным решением
        ally_formation = Formation(self.__all_vehicles, self.__me, ownership=Ownership.ALLY)
        yc, xc = ally_formation.find_geometrical_center()
        f = Formation(self.__all_vehicles, self.__me, ownership=Ownership.ENEMY, distance_limit=(xc, yc, 512))
        return f.get_count() > 10
