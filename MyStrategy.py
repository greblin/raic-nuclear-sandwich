from model.Game import Game
from model.Move import Move
from model.Player import Player
from model.World import World
from model.ActionType import ActionType

from Initializer import Initializer
from ActionQueue import ActionQueue

from ActionStrategy import ActionStrategy
from NaiveStrategy import NaiveStrategy


class MyStrategy:
    game = None
    world = None
    me = None

    vehicleById = {}
    updateTickByVehicleId = {}
    updatedVehicleXY = {}
    allVehicles = []

    initializer = None
    actionQueue = None

    strategy = None

    def initialize_strategy(self):
        self.initializer = Initializer(self.world)
        self.actionQueue = ActionQueue(self.world)

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
                self.strategy = NaiveStrategy(self.actionQueue, self.world)
            else:
                self.strategy = NaiveStrategy(self.actionQueue, self.world)

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










