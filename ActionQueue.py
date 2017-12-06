from collections import deque
from model.ActionType import ActionType
from model.World import World


class ActionQueue:
    __last_action_tick = []
    __action_in_queue = []

    def __init__(self, world: World):
        self.queue = deque([])
        self.world = world
        for i in range(ActionType.TACTICAL_NUCLEAR_STRIKE + 1):
            self.__last_action_tick.insert(i, None)
            self.__action_in_queue.insert(i, 0)

    def pop(self, world: World):
        action = None
        if len(self.queue) > 0:
            action = self.queue.popleft()
            action_name = action['action']
            self.__action_in_queue[action_name] = self.__action_in_queue[action_name] - 1
            self.__last_action_tick[action_name] = world.tick_index
            # print('POP: ', action)
        return action

    def push(self, action):
        # print('PUSH: ', action)
        action_name = action['action']
        self.__action_in_queue[action_name] = self.__action_in_queue[action_name] + 1
        self.queue.append(action)

    def clear(self):
        for i in range(ActionType.TACTICAL_NUCLEAR_STRIKE + 1):
            self.__action_in_queue.insert(i, 0)
        self.queue.clear()

    def get_last_action_tick(self, action):
        return self.__last_action_tick[action]

    def is_action_in_queue(self, action):
        return self.__action_in_queue[action] > 0
