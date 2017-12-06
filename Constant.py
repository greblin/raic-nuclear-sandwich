from model.VehicleType import VehicleType
from model.WeatherType import WeatherType
from model.TerrainType import TerrainType


class Constant:
    WORLD_SIZE = 1024

    # Размер логической матрицы первичного формирования
    INITIAL_MATRIX_ROWS_COUNT = 3
    INITIAL_MATRIX_COLS_COUNT = 3

    # Параметры первичного формирования
    INITIAL_ROW = 1
    INITIAL_FORMATION_UNITS_COUNT = 10

    # Размеры клеток физической матрицы первичного формирования
    CELL_DELIMITER_SIZE = 16
    CELL_SIZE = 58  # 10 * 4 + 9 * 2
    CELL_TOTAL_SIZE = CELL_SIZE + CELL_DELIMITER_SIZE

    # Размеры юнитов
    UNIT_RADIUS = 2
    UNIT_INITIAL_DISTANCE = 2

    # Массивы типов войск
    ALL_FORCE_TYPES = [VehicleType.ARRV, VehicleType.FIGHTER, VehicleType.HELICOPTER, VehicleType.IFV, VehicleType.TANK]
    GROUND_FORCE_TYPES = [VehicleType.TANK, VehicleType.IFV, VehicleType.ARRV]
    AIR_FORCE_TYPES = [VehicleType.HELICOPTER, VehicleType.FIGHTER]

    # Массивы базовых характеристик войск
    MAX_SPEED = {
        VehicleType.ARRV: 0.4,
        VehicleType.FIGHTER: 1.2,
        VehicleType.HELICOPTER: 0.9,
        VehicleType.IFV: 0.4,
        VehicleType.TANK: 0.3
    }

    # Массивы характеристик погоды
    WEATHER_SPEED_FACTOR = {
        WeatherType.CLEAR: 1,
        WeatherType.CLOUD: 0.8,
        WeatherType.RAIN: 0.6
    }

    # Массивы характеристик местности
    TERRAIN_SPEED_FACTOR = {
        TerrainType.PLAIN: 1,
        TerrainType.SWAMP: 0.6,
        TerrainType.FOREST: 0.8
    }

    # Параметры карт территории и погоды
    WEATHER_MAP_CELL_SIZE = 32
    TERRAIN_MAP_CELL_SIZE = 32

    # Параметры составления бутерброда
    SANDWICH_UNCONSOLIDATE_FACTOR = 3
    SANDWICH_LINES = {
        2: [VehicleType.FIGHTER, VehicleType.TANK],
        1: [VehicleType.HELICOPTER, VehicleType.IFV],
        0: [VehicleType.ARRV]
    }
    SANDWICH_HORIZONTAL_GROUP_INDEX = 3
    SANDWICH_GROUP_COUNT = 10
    SANDWICH_GROUP_OFFSET = {1: 3, 2: 2, 3: 1, 4: 1, 5: 0, 6: -1, 7: -1, 8: -2, 9: -3, 10: -3}
