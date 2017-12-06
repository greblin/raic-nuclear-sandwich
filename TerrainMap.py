from CharacteristicMap import CharacteristicMap
from Constant import Constant

class TerrainMap(CharacteristicMap):

    def _terrain_to_speed_factor(self, weather):
        _map = Constant.TERRAIN_SPEED_FACTOR
        return _map[weather]

    def get_minimum_speed_factor_on_path(self, from_topleft, from_bottomright, to_topleft, to_bottomright):
        submap = self._get_map_on_path(from_topleft, from_bottomright, to_topleft, to_bottomright)
        return self._min(self._transform_submap_with_function(submap, self._terrain_to_speed_factor))