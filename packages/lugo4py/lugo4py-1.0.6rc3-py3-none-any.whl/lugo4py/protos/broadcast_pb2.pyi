import server_pb2 as _server_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WatcherRequest(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class StartRequest(_message.Message):
    __slots__ = ("watcher_uuid",)
    WATCHER_UUID_FIELD_NUMBER: _ClassVar[int]
    watcher_uuid: str
    def __init__(self, watcher_uuid: _Optional[str] = ...) -> None: ...

class GameEvent(_message.Message):
    __slots__ = ("game_snapshot", "new_player", "lost_player", "state_change", "goal", "game_over", "breakpoint", "debug_released")
    GAME_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    NEW_PLAYER_FIELD_NUMBER: _ClassVar[int]
    LOST_PLAYER_FIELD_NUMBER: _ClassVar[int]
    STATE_CHANGE_FIELD_NUMBER: _ClassVar[int]
    GOAL_FIELD_NUMBER: _ClassVar[int]
    GAME_OVER_FIELD_NUMBER: _ClassVar[int]
    BREAKPOINT_FIELD_NUMBER: _ClassVar[int]
    DEBUG_RELEASED_FIELD_NUMBER: _ClassVar[int]
    game_snapshot: _server_pb2.GameSnapshot
    new_player: EventNewPlayer
    lost_player: EventLostPlayer
    state_change: EventStateChange
    goal: EventGoal
    game_over: EventGameOver
    breakpoint: EventDebugBreakpoint
    debug_released: EventDebugReleased
    def __init__(self, game_snapshot: _Optional[_Union[_server_pb2.GameSnapshot, _Mapping]] = ..., new_player: _Optional[_Union[EventNewPlayer, _Mapping]] = ..., lost_player: _Optional[_Union[EventLostPlayer, _Mapping]] = ..., state_change: _Optional[_Union[EventStateChange, _Mapping]] = ..., goal: _Optional[_Union[EventGoal, _Mapping]] = ..., game_over: _Optional[_Union[EventGameOver, _Mapping]] = ..., breakpoint: _Optional[_Union[EventDebugBreakpoint, _Mapping]] = ..., debug_released: _Optional[_Union[EventDebugReleased, _Mapping]] = ...) -> None: ...

class GameSetup(_message.Message):
    __slots__ = ("protocol_version", "dev_mode", "start_mode", "listening_mode", "listening_duration", "game_duration", "home_team", "away_team")
    class StartingMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NO_WAIT: _ClassVar[GameSetup.StartingMode]
        WAIT: _ClassVar[GameSetup.StartingMode]
    NO_WAIT: GameSetup.StartingMode
    WAIT: GameSetup.StartingMode
    class ListeningMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TIMER: _ClassVar[GameSetup.ListeningMode]
        RUSH: _ClassVar[GameSetup.ListeningMode]
        REMOTE: _ClassVar[GameSetup.ListeningMode]
    TIMER: GameSetup.ListeningMode
    RUSH: GameSetup.ListeningMode
    REMOTE: GameSetup.ListeningMode
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    DEV_MODE_FIELD_NUMBER: _ClassVar[int]
    START_MODE_FIELD_NUMBER: _ClassVar[int]
    LISTENING_MODE_FIELD_NUMBER: _ClassVar[int]
    LISTENING_DURATION_FIELD_NUMBER: _ClassVar[int]
    GAME_DURATION_FIELD_NUMBER: _ClassVar[int]
    HOME_TEAM_FIELD_NUMBER: _ClassVar[int]
    AWAY_TEAM_FIELD_NUMBER: _ClassVar[int]
    protocol_version: str
    dev_mode: bool
    start_mode: GameSetup.StartingMode
    listening_mode: GameSetup.ListeningMode
    listening_duration: int
    game_duration: int
    home_team: TeamSettings
    away_team: TeamSettings
    def __init__(self, protocol_version: _Optional[str] = ..., dev_mode: bool = ..., start_mode: _Optional[_Union[GameSetup.StartingMode, str]] = ..., listening_mode: _Optional[_Union[GameSetup.ListeningMode, str]] = ..., listening_duration: _Optional[int] = ..., game_duration: _Optional[int] = ..., home_team: _Optional[_Union[TeamSettings, _Mapping]] = ..., away_team: _Optional[_Union[TeamSettings, _Mapping]] = ...) -> None: ...

class TeamSettings(_message.Message):
    __slots__ = ("name", "avatar", "colors")
    NAME_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    COLORS_FIELD_NUMBER: _ClassVar[int]
    name: str
    avatar: str
    colors: TeamColors
    def __init__(self, name: _Optional[str] = ..., avatar: _Optional[str] = ..., colors: _Optional[_Union[TeamColors, _Mapping]] = ...) -> None: ...

class TeamColors(_message.Message):
    __slots__ = ("primary", "secondary")
    PRIMARY_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_FIELD_NUMBER: _ClassVar[int]
    primary: TeamColor
    secondary: TeamColor
    def __init__(self, primary: _Optional[_Union[TeamColor, _Mapping]] = ..., secondary: _Optional[_Union[TeamColor, _Mapping]] = ...) -> None: ...

class TeamColor(_message.Message):
    __slots__ = ("red", "green", "blue")
    RED_FIELD_NUMBER: _ClassVar[int]
    GREEN_FIELD_NUMBER: _ClassVar[int]
    BLUE_FIELD_NUMBER: _ClassVar[int]
    red: int
    green: int
    blue: int
    def __init__(self, red: _Optional[int] = ..., green: _Optional[int] = ..., blue: _Optional[int] = ...) -> None: ...

class EventNewPlayer(_message.Message):
    __slots__ = ("player",)
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    player: _server_pb2.Player
    def __init__(self, player: _Optional[_Union[_server_pb2.Player, _Mapping]] = ...) -> None: ...

class EventLostPlayer(_message.Message):
    __slots__ = ("player",)
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    player: _server_pb2.Player
    def __init__(self, player: _Optional[_Union[_server_pb2.Player, _Mapping]] = ...) -> None: ...

class EventStateChange(_message.Message):
    __slots__ = ("previous_state", "new_state")
    PREVIOUS_STATE_FIELD_NUMBER: _ClassVar[int]
    NEW_STATE_FIELD_NUMBER: _ClassVar[int]
    previous_state: _server_pb2.GameSnapshot.State
    new_state: _server_pb2.GameSnapshot.State
    def __init__(self, previous_state: _Optional[_Union[_server_pb2.GameSnapshot.State, str]] = ..., new_state: _Optional[_Union[_server_pb2.GameSnapshot.State, str]] = ...) -> None: ...

class EventGoal(_message.Message):
    __slots__ = ("side",)
    SIDE_FIELD_NUMBER: _ClassVar[int]
    side: _server_pb2.Team.Side
    def __init__(self, side: _Optional[_Union[_server_pb2.Team.Side, str]] = ...) -> None: ...

class EventGameOver(_message.Message):
    __slots__ = ("reason", "blame")
    class EndingReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TIME_IS_OVER: _ClassVar[EventGameOver.EndingReason]
        WAITING_EXPIRED: _ClassVar[EventGameOver.EndingReason]
        NO_ENOUGH_PLAYER: _ClassVar[EventGameOver.EndingReason]
        EXTERNAL_REQUEST: _ClassVar[EventGameOver.EndingReason]
        KNOCKOUT: _ClassVar[EventGameOver.EndingReason]
    TIME_IS_OVER: EventGameOver.EndingReason
    WAITING_EXPIRED: EventGameOver.EndingReason
    NO_ENOUGH_PLAYER: EventGameOver.EndingReason
    EXTERNAL_REQUEST: EventGameOver.EndingReason
    KNOCKOUT: EventGameOver.EndingReason
    class BlameStop(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NORMAL: _ClassVar[EventGameOver.BlameStop]
        BOTH_TEAMS: _ClassVar[EventGameOver.BlameStop]
        HOME_TEAM: _ClassVar[EventGameOver.BlameStop]
        AWAY_TEAM: _ClassVar[EventGameOver.BlameStop]
    NORMAL: EventGameOver.BlameStop
    BOTH_TEAMS: EventGameOver.BlameStop
    HOME_TEAM: EventGameOver.BlameStop
    AWAY_TEAM: EventGameOver.BlameStop
    REASON_FIELD_NUMBER: _ClassVar[int]
    BLAME_FIELD_NUMBER: _ClassVar[int]
    reason: EventGameOver.EndingReason
    blame: EventGameOver.BlameStop
    def __init__(self, reason: _Optional[_Union[EventGameOver.EndingReason, str]] = ..., blame: _Optional[_Union[EventGameOver.BlameStop, str]] = ...) -> None: ...

class EventDebugBreakpoint(_message.Message):
    __slots__ = ("breakpoint",)
    class Breakpoint(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ORDERS: _ClassVar[EventDebugBreakpoint.Breakpoint]
        TURN: _ClassVar[EventDebugBreakpoint.Breakpoint]
    ORDERS: EventDebugBreakpoint.Breakpoint
    TURN: EventDebugBreakpoint.Breakpoint
    BREAKPOINT_FIELD_NUMBER: _ClassVar[int]
    breakpoint: EventDebugBreakpoint.Breakpoint
    def __init__(self, breakpoint: _Optional[_Union[EventDebugBreakpoint.Breakpoint, str]] = ...) -> None: ...

class EventDebugReleased(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
