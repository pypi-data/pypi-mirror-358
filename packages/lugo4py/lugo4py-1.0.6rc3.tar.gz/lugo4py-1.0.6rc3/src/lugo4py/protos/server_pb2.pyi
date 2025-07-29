import physics_pb2 as _physics_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JoinRequest(_message.Message):
    __slots__ = ("token", "protocol_version", "team_side", "number", "init_position")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    TEAM_SIDE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    INIT_POSITION_FIELD_NUMBER: _ClassVar[int]
    token: str
    protocol_version: str
    team_side: Team.Side
    number: int
    init_position: _physics_pb2.Point
    def __init__(self, token: _Optional[str] = ..., protocol_version: _Optional[str] = ..., team_side: _Optional[_Union[Team.Side, str]] = ..., number: _Optional[int] = ..., init_position: _Optional[_Union[_physics_pb2.Point, _Mapping]] = ...) -> None: ...

class GameSnapshot(_message.Message):
    __slots__ = ("state", "turn", "home_team", "away_team", "ball", "turns_ball_in_goal_zone", "shot_clock")
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        WAITING: _ClassVar[GameSnapshot.State]
        GET_READY: _ClassVar[GameSnapshot.State]
        LISTENING: _ClassVar[GameSnapshot.State]
        PLAYING: _ClassVar[GameSnapshot.State]
        SHIFTING: _ClassVar[GameSnapshot.State]
        OVER: _ClassVar[GameSnapshot.State]
    WAITING: GameSnapshot.State
    GET_READY: GameSnapshot.State
    LISTENING: GameSnapshot.State
    PLAYING: GameSnapshot.State
    SHIFTING: GameSnapshot.State
    OVER: GameSnapshot.State
    STATE_FIELD_NUMBER: _ClassVar[int]
    TURN_FIELD_NUMBER: _ClassVar[int]
    HOME_TEAM_FIELD_NUMBER: _ClassVar[int]
    AWAY_TEAM_FIELD_NUMBER: _ClassVar[int]
    BALL_FIELD_NUMBER: _ClassVar[int]
    TURNS_BALL_IN_GOAL_ZONE_FIELD_NUMBER: _ClassVar[int]
    SHOT_CLOCK_FIELD_NUMBER: _ClassVar[int]
    state: GameSnapshot.State
    turn: int
    home_team: Team
    away_team: Team
    ball: Ball
    turns_ball_in_goal_zone: int
    shot_clock: ShotClock
    def __init__(self, state: _Optional[_Union[GameSnapshot.State, str]] = ..., turn: _Optional[int] = ..., home_team: _Optional[_Union[Team, _Mapping]] = ..., away_team: _Optional[_Union[Team, _Mapping]] = ..., ball: _Optional[_Union[Ball, _Mapping]] = ..., turns_ball_in_goal_zone: _Optional[int] = ..., shot_clock: _Optional[_Union[ShotClock, _Mapping]] = ...) -> None: ...

class Team(_message.Message):
    __slots__ = ("players", "name", "score", "side")
    class Side(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HOME: _ClassVar[Team.Side]
        AWAY: _ClassVar[Team.Side]
    HOME: Team.Side
    AWAY: Team.Side
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    players: _containers.RepeatedCompositeFieldContainer[Player]
    name: str
    score: int
    side: Team.Side
    def __init__(self, players: _Optional[_Iterable[_Union[Player, _Mapping]]] = ..., name: _Optional[str] = ..., score: _Optional[int] = ..., side: _Optional[_Union[Team.Side, str]] = ...) -> None: ...

class ShotClock(_message.Message):
    __slots__ = ("team_side", "remaining_turns")
    TEAM_SIDE_FIELD_NUMBER: _ClassVar[int]
    REMAINING_TURNS_FIELD_NUMBER: _ClassVar[int]
    team_side: Team.Side
    remaining_turns: int
    def __init__(self, team_side: _Optional[_Union[Team.Side, str]] = ..., remaining_turns: _Optional[int] = ...) -> None: ...

class Player(_message.Message):
    __slots__ = ("number", "position", "velocity", "team_side", "init_position", "is_jumping")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    TEAM_SIDE_FIELD_NUMBER: _ClassVar[int]
    INIT_POSITION_FIELD_NUMBER: _ClassVar[int]
    IS_JUMPING_FIELD_NUMBER: _ClassVar[int]
    number: int
    position: _physics_pb2.Point
    velocity: _physics_pb2.Velocity
    team_side: Team.Side
    init_position: _physics_pb2.Point
    is_jumping: bool
    def __init__(self, number: _Optional[int] = ..., position: _Optional[_Union[_physics_pb2.Point, _Mapping]] = ..., velocity: _Optional[_Union[_physics_pb2.Velocity, _Mapping]] = ..., team_side: _Optional[_Union[Team.Side, str]] = ..., init_position: _Optional[_Union[_physics_pb2.Point, _Mapping]] = ..., is_jumping: bool = ...) -> None: ...

class Ball(_message.Message):
    __slots__ = ("position", "velocity", "holder")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    position: _physics_pb2.Point
    velocity: _physics_pb2.Velocity
    holder: Player
    def __init__(self, position: _Optional[_Union[_physics_pb2.Point, _Mapping]] = ..., velocity: _Optional[_Union[_physics_pb2.Velocity, _Mapping]] = ..., holder: _Optional[_Union[Player, _Mapping]] = ...) -> None: ...

class OrderResponse(_message.Message):
    __slots__ = ("code", "details")
    class StatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[OrderResponse.StatusCode]
        UNKNOWN_PLAYER: _ClassVar[OrderResponse.StatusCode]
        NOT_LISTENING: _ClassVar[OrderResponse.StatusCode]
        WRONG_TURN: _ClassVar[OrderResponse.StatusCode]
        OTHER: _ClassVar[OrderResponse.StatusCode]
    SUCCESS: OrderResponse.StatusCode
    UNKNOWN_PLAYER: OrderResponse.StatusCode
    NOT_LISTENING: OrderResponse.StatusCode
    WRONG_TURN: OrderResponse.StatusCode
    OTHER: OrderResponse.StatusCode
    CODE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    code: OrderResponse.StatusCode
    details: str
    def __init__(self, code: _Optional[_Union[OrderResponse.StatusCode, str]] = ..., details: _Optional[str] = ...) -> None: ...

class OrderSet(_message.Message):
    __slots__ = ("turn", "orders", "debug_message")
    TURN_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    DEBUG_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    turn: int
    orders: _containers.RepeatedCompositeFieldContainer[Order]
    debug_message: str
    def __init__(self, turn: _Optional[int] = ..., orders: _Optional[_Iterable[_Union[Order, _Mapping]]] = ..., debug_message: _Optional[str] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("move", "catch", "kick", "jump")
    MOVE_FIELD_NUMBER: _ClassVar[int]
    CATCH_FIELD_NUMBER: _ClassVar[int]
    KICK_FIELD_NUMBER: _ClassVar[int]
    JUMP_FIELD_NUMBER: _ClassVar[int]
    move: Move
    catch: Catch
    kick: Kick
    jump: Jump
    def __init__(self, move: _Optional[_Union[Move, _Mapping]] = ..., catch: _Optional[_Union[Catch, _Mapping]] = ..., kick: _Optional[_Union[Kick, _Mapping]] = ..., jump: _Optional[_Union[Jump, _Mapping]] = ...) -> None: ...

class Move(_message.Message):
    __slots__ = ("velocity",)
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    velocity: _physics_pb2.Velocity
    def __init__(self, velocity: _Optional[_Union[_physics_pb2.Velocity, _Mapping]] = ...) -> None: ...

class Catch(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Kick(_message.Message):
    __slots__ = ("velocity",)
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    velocity: _physics_pb2.Velocity
    def __init__(self, velocity: _Optional[_Union[_physics_pb2.Velocity, _Mapping]] = ...) -> None: ...

class Jump(_message.Message):
    __slots__ = ("velocity",)
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    velocity: _physics_pb2.Velocity
    def __init__(self, velocity: _Optional[_Union[_physics_pb2.Velocity, _Mapping]] = ...) -> None: ...
