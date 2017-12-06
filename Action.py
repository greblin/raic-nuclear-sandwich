from model.ActionType import ActionType
from Constant import Constant

class Action:
    @staticmethod
    def clear_and_select(topleft=(0, 0), bottomright=(None, None), vehicle_type=None, group=0):
        return {
            'action':       ActionType.CLEAR_AND_SELECT,
            'group':        group,
            'top':          topleft[0],
            'left':         topleft[1],
            'bottom':       Constant.WORLD_SIZE if bottomright[0] is None else bottomright[0],
            'right':        Constant.WORLD_SIZE if bottomright[1] is None else bottomright[1],
            'vehicle_type': vehicle_type
        }

    @staticmethod
    def move(x, y, max_speed=0):
        return {
            'action':    ActionType.MOVE,
            'x':         x,
            'y':         y,
            'max_speed': max_speed
        }

    @staticmethod
    def scale(x, y, factor, max_speed=0):
        return {
            'action':    ActionType.SCALE,
            'x':         x,
            'y':         y,
            'factor':    factor,
            'max_speed': max_speed
        }

    @staticmethod
    def assign(group):
        return {
            'action': ActionType.ASSIGN,
            'group':  group
        }

    @staticmethod
    def rotate(x, y, angle, max_speed=0, max_angular_speed=0):
        return {
            'action':            ActionType.ROTATE,
            'x':                 x,
            'y':                 y,
            'angle':             angle,
            'max_speed':         max_speed,
            'max_angular_speed': max_angular_speed
        }

    @staticmethod
    def nuclear_strike(x, y, highlighter_id):
        return {
            'action':     ActionType.TACTICAL_NUCLEAR_STRIKE,
            'x':          x,
            'y':          y,
            'vehicle_id': highlighter_id
        }
