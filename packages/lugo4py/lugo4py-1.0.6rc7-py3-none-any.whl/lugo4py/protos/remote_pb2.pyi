import physics_pb2 as _physics_pb2
import server_pb2 as _server_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PauseResumeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NextTurnRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NextOrderRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BallProperties(_message.Message):
    __slots__ = ("position", "velocity", "holder")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    HOLDER_FIELD_NUMBER: _ClassVar[int]
    position: _physics_pb2.Point
    velocity: _physics_pb2.Velocity
    holder: _server_pb2.Player
    def __init__(self, position: _Optional[_Union[_physics_pb2.Point, _Mapping]] = ..., velocity: _Optional[_Union[_physics_pb2.Velocity, _Mapping]] = ..., holder: _Optional[_Union[_server_pb2.Player, _Mapping]] = ...) -> None: ...

class PlayerProperties(_message.Message):
    __slots__ = ("side", "number", "position", "velocity")
    SIDE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    side: _server_pb2.Team.Side
    number: int
    position: _physics_pb2.Point
    velocity: _physics_pb2.Velocity
    def __init__(self, side: _Optional[_Union[_server_pb2.Team.Side, str]] = ..., number: _Optional[int] = ..., position: _Optional[_Union[_physics_pb2.Point, _Mapping]] = ..., velocity: _Optional[_Union[_physics_pb2.Velocity, _Mapping]] = ...) -> None: ...

class GameProperties(_message.Message):
    __slots__ = ("turn", "home_score", "away_score", "frame_interval", "shot_clock")
    TURN_FIELD_NUMBER: _ClassVar[int]
    HOME_SCORE_FIELD_NUMBER: _ClassVar[int]
    AWAY_SCORE_FIELD_NUMBER: _ClassVar[int]
    FRAME_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    SHOT_CLOCK_FIELD_NUMBER: _ClassVar[int]
    turn: int
    home_score: int
    away_score: int
    frame_interval: int
    shot_clock: _server_pb2.ShotClock
    def __init__(self, turn: _Optional[int] = ..., home_score: _Optional[int] = ..., away_score: _Optional[int] = ..., frame_interval: _Optional[int] = ..., shot_clock: _Optional[_Union[_server_pb2.ShotClock, _Mapping]] = ...) -> None: ...

class CommandResponse(_message.Message):
    __slots__ = ("code", "game_snapshot", "details")
    class StatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[CommandResponse.StatusCode]
        INVALID_VALUE: _ClassVar[CommandResponse.StatusCode]
        DEADLINE_EXCEEDED: _ClassVar[CommandResponse.StatusCode]
        OTHER: _ClassVar[CommandResponse.StatusCode]
    SUCCESS: CommandResponse.StatusCode
    INVALID_VALUE: CommandResponse.StatusCode
    DEADLINE_EXCEEDED: CommandResponse.StatusCode
    OTHER: CommandResponse.StatusCode
    CODE_FIELD_NUMBER: _ClassVar[int]
    GAME_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    code: CommandResponse.StatusCode
    game_snapshot: _server_pb2.GameSnapshot
    details: str
    def __init__(self, code: _Optional[_Union[CommandResponse.StatusCode, str]] = ..., game_snapshot: _Optional[_Union[_server_pb2.GameSnapshot, _Mapping]] = ..., details: _Optional[str] = ...) -> None: ...

class ResumeListeningRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResumeListeningResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResetPlayerPositionsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResetGameRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResetPlayerPositionsResponse(_message.Message):
    __slots__ = ("game_snapshot",)
    GAME_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    game_snapshot: _server_pb2.GameSnapshot
    def __init__(self, game_snapshot: _Optional[_Union[_server_pb2.GameSnapshot, _Mapping]] = ...) -> None: ...

class GameSnapshotRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GameSnapshotResponse(_message.Message):
    __slots__ = ("game_snapshot",)
    GAME_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    game_snapshot: _server_pb2.GameSnapshot
    def __init__(self, game_snapshot: _Optional[_Union[_server_pb2.GameSnapshot, _Mapping]] = ...) -> None: ...
