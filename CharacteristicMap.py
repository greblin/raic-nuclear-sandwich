class CharacteristicMap:
    __map = None
    __cell_size = None

    def __init__(self, characteristic_map, cell_size):
        self.__map = characteristic_map
        self.__cell_size = cell_size

    def _transform_real_coords_to_map_coords(self, y, x):
        return round(y) // self.__cell_size, round(x) // self.__cell_size

    def _get_map_on_path(self, from_topleft, from_bottomright, to_topleft, to_bottomright):
        from_i_topleft, from_j_topleft = self._transform_real_coords_to_map_coords(*from_topleft)
        from_i_bottomright, from_j_bottomright = self._transform_real_coords_to_map_coords(*from_bottomright)
        to_i_topleft, to_j_topleft = self._transform_real_coords_to_map_coords(*to_topleft)
        to_i_bottomright, to_j_bottomright = self._transform_real_coords_to_map_coords(*to_bottomright)
        i_topleft, j_topleft = min(from_i_topleft, to_i_topleft), min(from_j_topleft, to_j_topleft)
        i_bottomright, j_bottomright = max(from_i_bottomright, to_i_bottomright), max(from_j_bottomright, to_j_bottomright)
        submap = {}
        for i in range(i_topleft, i_bottomright+1):
            rowmap = {}
            for j in range(j_topleft, j_bottomright+1):
                rowmap[j] = self.__map[j][i]
            submap[i] = rowmap
        return submap

    def _transform_submap_with_function(self, submap, f):
        result = {}
        for i, row in submap.items():
            result[i] = {}
            for j, value in row.items():
                result[i][j] = f(value)
        return result

    def _min(self, submap):
        min_value = None
        for i, row in submap.items():
            for j, value in row.items():
                min_value = value if min_value is None or value < min_value else min_value
        return min_value