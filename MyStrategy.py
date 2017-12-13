from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.World import World
from model.ActionType import ActionType
import math

from Constant import Constant
from Initializer import Initializer
from ActionQueue import ActionQueue
from Action import Action
from WeatherMap import WeatherMap
from TerrainMap import TerrainMap
from ActionStrategy import ActionStrategy
from NaiveStrategy import NaiveStrategy
from Formation import Formation
from Ownership import Ownership

class MyStrategy:
    game = None
    world = None
    me = None

    __weather_map = None
    __terrain_map = None

    vehicleById = {}
    updateTickByVehicleId = {}
    updatedVehicleXY = {}
    allVehicles = []

    initializer = None
    actionQueue = None

    strategy = None

    _sos_mode = False

    def initialize_strategy(self):
        self.initializer = Initializer(self.world)
        self.actionQueue = ActionQueue(self.world)
        self.__weather_map = WeatherMap(self.world.weather_by_cell_x_y, Constant.WEATHER_MAP_CELL_SIZE)
        self.__terrain_map = TerrainMap(self.world.terrain_by_cell_x_y, Constant.TERRAIN_MAP_CELL_SIZE)

    def initialize_tick(self):
        self.updatedVehicleXY = {}
        for vehicle in self.world.new_vehicles:
            self.vehicleById[vehicle.id] = vehicle
            self.updateTickByVehicleId[vehicle.id] = self.world.tick_index
        for vehicleUpdate in self.world.vehicle_updates:
            vehicleId = vehicleUpdate.id
            if vehicleUpdate.durability == 0:
                self.vehicleById.pop(vehicleId)
                self.updateTickByVehicleId.pop(vehicleId)
            else:
                x_old, y_old = self.vehicleById[vehicleId].x, self.vehicleById[vehicleId].y
                self.vehicleById[vehicleId].update(vehicleUpdate)
                x_new, y_new = self.vehicleById[vehicleId].x, self.vehicleById[vehicleId].y
                if self.vehicleById[vehicleId].player_id == self.me.id and (x_old != x_new or y_old != y_new):
                    self.updatedVehicleXY[vehicleId] = (x_new - x_old, y_new - y_old)
                self.updateTickByVehicleId[vehicleId] = self.world.tick_index
        self.allVehicles = list(self.vehicleById.values())

    def execute_action(self, move: Move, action: dict):
        for field, value in action.items():
            setattr(move, field, value)
        return True

    def execute_delayed_action(self, move: Move, world: World):
        action = self.actionQueue.pop(world)
        if action is None:
            return False
        return self.execute_action(move, action)

    def move(self, me: Player, world: World, game: Game, move: Move):
        self.game = game
        self.world = world
        self.me = me
        if world.tick_index == 0:
            self.initialize_strategy()
        self.initialize_tick()

        if self.strategy is None:
            if self.initializer.current_step not in [Initializer.STEP_STOP, Initializer.STEP_INTERRUPT_STOP]:
                self.initializer.prepare_step(self.me, self.world, self.allVehicles)
                self.initializer.perform_current_step(self.actionQueue, self.updatedVehicleXY)
            elif self.initializer.current_step == Initializer.STEP_INTERRUPT_STOP:
                self.strategy = NaiveStrategy(self.actionQueue, self.world, self.__weather_map, self.__terrain_map)
            else:
                self.strategy = NaiveStrategy(self.actionQueue, self.world, self.__weather_map, self.__terrain_map)

        if self.strategy:
        #if False:
            if not self._sos_mode:
                if self.__save_our_souls(world):
                    return
            else:
                if self.__comeback_after_strike(world):
                    return

        if me.remaining_action_cooldown_ticks > 0:
            return
        if self.execute_delayed_action(move, world):
            return
        self.determine_following_actions()
        self.execute_delayed_action(move, world)

    def determine_following_actions(self):
        if self.strategy is None:
            return
        self.strategy.initialize_tick(self.game, self.world, self.me, self.allVehicles, self.updateTickByVehicleId)
        self.strategy.determine_following_actions(self.updatedVehicleXY)

    def __save_our_souls(self, world: World):
        opponent = world.get_opponent_player()
        next_nuclear_strike_tick = opponent.next_nuclear_strike_tick_index
        if next_nuclear_strike_tick == -1:
            return False
        f = Formation(self.allVehicles, self.me, ownership=Ownership.ALLY)
        x = opponent.next_nuclear_strike_x
        y = opponent.next_nuclear_strike_y

        next_nuclear_strike_vehicle_id = opponent.next_nuclear_strike_vehicle_id
        if next_nuclear_strike_vehicle_id == -1:
            return False
        if next_nuclear_strike_vehicle_id not in self.vehicleById:
            return False
        is_aerial = self.vehicleById[next_nuclear_strike_vehicle_id].aerial

        kill_factor = f.calc_nuclear_kill_factor(x, y)
        if kill_factor['total_damage'] < 1200 and kill_factor['survived'] > kill_factor['killed'] * 5 and not is_aerial:
            return False

        from_x, from_y = self.vehicleById[next_nuclear_strike_vehicle_id].x, self.vehicleById[next_nuclear_strike_vehicle_id].y
        sos_vector = (y - from_y, x - from_x)
        sos_vector_norm = 120 / math.hypot(sos_vector[0], sos_vector[1])
        sos_vector = (sos_vector[0] * sos_vector_norm, sos_vector[1] * sos_vector_norm)
        topleft = f.find_topleft()
        bottomright = f.find_bottomright()
        if topleft[0] + sos_vector[0] < 0 or topleft[1] + sos_vector[1] < 0:
            sos_vector = (-sos_vector[0], -sos_vector[1])
        elif bottomright[0] + sos_vector[0] >= self.world.height or bottomright[1] + sos_vector[1] >= self.world.width:
            sos_vector = (-sos_vector[0], -sos_vector[1])
        self.actionQueue.clear()
        self.actionQueue.push(Action.move(sos_vector[1], sos_vector[0], 0.3))
        self._sos_mode = True
        return True

    def __comeback_after_strike(self, world: World):
        opponent = world.get_opponent_player()
        next_nuclear_strike_tick = opponent.next_nuclear_strike_tick_index
        if next_nuclear_strike_tick != -1:
            return False
        if not self.actionQueue.is_action_in_queue(ActionType.MOVE):
            self.actionQueue.push(Action.move(0, 0))
        else:
            self.actionQueue.clear()
        self._sos_mode = False
        return True
