from ...mapper import Mapper
from ..loader import EnvVarLoader
from ...protos.physics_pb2 import Point
from typing import Tuple

def DefaultInitBundle() -> Tuple[EnvVarLoader, Mapper, Point]:
    defaultConfig = EnvVarLoader()

    defaultMapper = Mapper(10, 6, defaultConfig.get_bot_team_side())

    initialRegion = defaultMapper.get_region(DEFAULT_PLAYER_POSITIONS[defaultConfig.get_bot_number()]["Col"], DEFAULT_PLAYER_POSITIONS[defaultConfig.get_bot_number()]["Row"])

    defaultInitialPosition = initialRegion.get_center()

    return [ defaultConfig, defaultMapper, defaultInitialPosition]

DEFAULT_PLAYER_POSITIONS = {
    1: {"Col": 0, "Row": 0},
    2: {"Col": 1, "Row": 1},
    3: {"Col": 2, "Row": 2},
    4: {"Col": 2, "Row": 3},
    5: {"Col": 1, "Row": 4},
    6: {"Col": 3, "Row": 1},
    7: {"Col": 3, "Row": 2},
    8: {"Col": 3, "Row": 3},
    9: {"Col": 3, "Row": 4},
    10: {"Col": 4, "Row": 3},
    11: {"Col": 4, "Row": 2},
}
