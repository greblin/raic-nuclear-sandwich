from model.Game import Game
from model.World import World
from model.Player import Player

from ActionQueue import ActionQueue

class ActionStrategy:
    game = None
    world = None
    me = None

    strategyTick = -1
    strategyStartTick = 0

    actionQueue = None

    vehicleById = {}
    updateTickByVehicleId = {}
    allVehicles = []

    def __init__(self, action_queue: ActionQueue, world: World):
        self.actionQueue = action_queue
        self.strategyStartTick = world.tick_index

    def initialize_tick(self, game: Game, world: World, me: Player, all_vehicles, update_tick_by_vehicle_id):
        self.game = game
        self.world = world
        self.me = me
        self.strategyTick = self.strategyTick + 1
        self.allVehicles = all_vehicles
        self.updateTickByVehicleId = update_tick_by_vehicle_id

    def determine_following_actions(self):
        pass