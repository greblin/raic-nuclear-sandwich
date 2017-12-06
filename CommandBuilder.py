from model.Player import Player

from WeatherMap import WeatherMap
from TerrainMap import TerrainMap


class CommandBuilder:
    _me = None
    _weather_map = None
    _terrain_map = None
    _all_vehicles = None

    def __init__(self, me: Player, weather_map: WeatherMap, terrain_map: TerrainMap, all_vehicles):
        self._me = me
        self._weather_map = weather_map
        self._terrain_map = terrain_map
        self._all_vehicles = all_vehicles

    def get_command_list(self):
        pass
