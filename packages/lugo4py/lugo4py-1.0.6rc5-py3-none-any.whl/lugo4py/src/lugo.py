"""
File: lugo.py
Author: Angelo Katipunan
Date: May 20, 2023
Description: This file mocks the gRPC methods to help IDEs intellisense.

Python gRPC files are not friendly to IDEs, what makes the intellisense experience very poor or, sometimes, impossible.

In order to help the programmer experience while developing bots, this file mocks the gRPC methods in a more friendly way.

In short, this file content is not used at all by the package, but will guide the IDE to help the devs.
If you are looking for the real implementation of these methods, please look at the `protos` directory (good luck on that)

"""

from enum import IntEnum
from typing import List

from ..protos.physics_pb2 import Velocity, Vector
from ..protos.server_pb2 import Team

def new_velocity(vector: Vector) -> Velocity:
    """
    Create a new Velocity object based on a Vector.

    This function takes a Vector object and creates a new Velocity object by setting its direction
    components based on the x and y components from the provided Vector.

    Args:
        vector (Vector): A Vector object representing the direction components.

    Returns:
        Velocity: A new Velocity object with the direction components set from the Vector.

    Example:
    vector = Vector(1.0, 0.0)
    velocity = new_velocity(vector)
    """
    v = Velocity()
    v.direction.x = vector.x
    v.direction.y = vector.y
    return v



class TeamSide(IntEnum):
    HOME = Team.Side.HOME
    AWAY = Team.Side.AWAY

