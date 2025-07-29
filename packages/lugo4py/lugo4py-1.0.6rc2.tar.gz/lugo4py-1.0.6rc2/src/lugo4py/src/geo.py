from ..protos import physics_pb2
from math import hypot


def new_vector(from_point: physics_pb2.Point, to_point: physics_pb2.Point):
    v = physics_pb2.Vector()
    v.x = to_point.x - from_point.x
    v.y = to_point.y - from_point.y
    if is_invalid_vector(v):
        raise RuntimeError("A vector cannot have zero length")
    return v


def normalize(v: physics_pb2.Vector):
    """
    Normalize a vector by scaling it to have a magnitude of 100 units.

    This function takes a vector and scales it so that its magnitude (length) becomes 100 units while maintaining its direction.

    Args:
        v (physics_pb2.Vector): The vector to be normalized.

    Returns:
        physics_pb2.Vector: The normalized vector with a magnitude of 100 units.

    Example:
    vector = physics_pb2.Vector(2.0, 2.0)
    normalized_vector = normalize(vector)
    """
    length = get_length(v)

    if length <= 0:
        raise RuntimeError("Vector cannot have zero length")
    return get_scaled_vector(v, 100 / length)


def get_length(v: physics_pb2.Vector):
    """
    Calculate the length (magnitude) of a vector.

    This function computes the length of a vector using the Pythagorean theorem, given its x and y components.

    Args:
        v (physics_pb2.Vector): The vector for which to calculate the length.

    Returns:
        float: The length (magnitude) of the vector.

    Example:
    vector = physics_pb2.Vector(3.0, 4.0)
    length = get_length(vector)
    # length will be 5.0
    """
    return hypot(v.x, v.y)


def get_scaled_vector(v: physics_pb2.Vector, scale: float):
    """
    Scale a vector by a specified factor.

    This function takes a vector and scales it by the provided scale factor, returning a new vector with scaled components.

    Args:
        v (physics_pb2.Vector): The vector to be scaled.
        scale (float): The scaling factor.

    Returns:
        physics_pb2.Vector: The scaled vector.

    Raises:
        RuntimeError: If the scale is less than or equal to 0, as it would result in a zero-length vector.

    Example:
    vector = physics_pb2.Vector(2.0, 2.0)
    scaled_vector = get_scaled_vector(vector, 2.5)
    """
    if scale <= 0:
        raise RuntimeError("Vector cannot have zero length")
    v2 = physics_pb2.Vector()
    v2.x = v.x * scale
    v2.y = v.y * scale
    return v2


def sub_vector(original_vector: physics_pb2.Vector, sub_vector: physics_pb2.Vector) -> physics_pb2.Vector:
    """
    Subtract one vector from another.

    This function subtracts the components of the sub_vector from the original_vector, resulting in a new vector.

    Args:
        original_vector (physics_pb2.Vector): The original vector.
        sub_vector (physics_pb2.Vector): The vector to be subtracted.

    Returns:
        physics_pb2.Vector: The resulting vector after subtraction.

    Raises:
        ValueError: If the subtraction would result in a zero-length vector.

    Example:
    original = physics_pb2.Vector(5.0, 5.0)
    subtract = physics_pb2.Vector(2.0, 3.0)
    result_vector = sub_vector(original, subtract)
    """
    new_x = original_vector.x - sub_vector.x
    new_y = original_vector.y - sub_vector.y

    new_vector = physics_pb2.Vector()
    new_vector.x = new_x
    new_vector.y = new_y

    if is_invalid_vector(new_vector):
        raise ValueError("Could not subtract vectors: the result would be a zero-length vector")
    return new_vector


def is_invalid_vector(v: physics_pb2.Vector) -> bool:
    """
    Check if a vector is invalid (zero-length).

    This function checks if a given vector has both components equal to zero, indicating it's a zero-length vector.

    Args:
        v (physics_pb2.Vector): The vector to be checked.

    Returns:
        bool: True if the vector is invalid (zero-length), otherwise False.

    Example:
    vector = physics_pb2.Vector(0.0, 0.0)
    is_invalid = is_invalid_vector(vector)
    """
    return v.x == 0 and v.y == 0


def distance_between_points(a: physics_pb2.Point, b: physics_pb2.Point):
    """
    Calculate the Euclidean distance between two points.

    This function computes the Euclidean distance between two points represented by Point objects.

    Args:
        a (Point): The first point.
        b (Point): The second point.

    Returns:
        float: The Euclidean distance between the two points.

    Example:
    point1 = Point(1, 2)
    point2 = Point(4, 6)
    distance = distance_between_points(point1, point2)
    """
    return hypot(a.x - b.x, a.y - b.y)

def new_zeroed_velocity(direction: physics_pb2.Vector):
    velocity = physics_pb2.Velocity()
    velocity.direction.x = direction.x
    velocity.direction.y = direction.y
    velocity.speed = 0
    return velocity

def target_from(v: physics_pb2.Vector, point: physics_pb2.Point):
    target = physics_pb2.Point()
    target.x = point.x + round(v.x)
    target.y = point.y + round(v.y)
    return target

def new_zeroed_point():
    point = physics_pb2.Point()
    point.x = 0
    point.y = 0
    return point
