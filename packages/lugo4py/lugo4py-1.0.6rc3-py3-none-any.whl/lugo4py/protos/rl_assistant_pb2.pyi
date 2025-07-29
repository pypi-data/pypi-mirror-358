import server_pb2 as _server_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RLSessionConfig(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PlayerOrdersOnRLSession(_message.Message):
    __slots__ = ("team_side", "number", "behaviour", "orders")
    TEAM_SIDE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    BEHAVIOUR_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    team_side: _server_pb2.Team.Side
    number: int
    behaviour: str
    orders: _containers.RepeatedCompositeFieldContainer[_server_pb2.Order]
    def __init__(self, team_side: _Optional[_Union[_server_pb2.Team.Side, str]] = ..., number: _Optional[int] = ..., behaviour: _Optional[str] = ..., orders: _Optional[_Iterable[_Union[_server_pb2.Order, _Mapping]]] = ...) -> None: ...

class PlayersOrders(_message.Message):
    __slots__ = ("default_behaviour", "players_orders")
    DEFAULT_BEHAVIOUR_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_ORDERS_FIELD_NUMBER: _ClassVar[int]
    default_behaviour: str
    players_orders: _containers.RepeatedCompositeFieldContainer[PlayerOrdersOnRLSession]
    def __init__(self, default_behaviour: _Optional[str] = ..., players_orders: _Optional[_Iterable[_Union[PlayerOrdersOnRLSession, _Mapping]]] = ...) -> None: ...

class TurnOutcome(_message.Message):
    __slots__ = ("game_snapshot", "score_changed", "shot_clock_expired", "goal_zone_timer_expired")
    GAME_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    SCORE_CHANGED_FIELD_NUMBER: _ClassVar[int]
    SHOT_CLOCK_EXPIRED_FIELD_NUMBER: _ClassVar[int]
    GOAL_ZONE_TIMER_EXPIRED_FIELD_NUMBER: _ClassVar[int]
    game_snapshot: _server_pb2.GameSnapshot
    score_changed: bool
    shot_clock_expired: bool
    goal_zone_timer_expired: bool
    def __init__(self, game_snapshot: _Optional[_Union[_server_pb2.GameSnapshot, _Mapping]] = ..., score_changed: bool = ..., shot_clock_expired: bool = ..., goal_zone_timer_expired: bool = ...) -> None: ...

class RLResetConfig(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
