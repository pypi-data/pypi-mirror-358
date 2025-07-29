from ..protos.physics_pb2 import Point
from ..protos.server_pb2 import Order, Team
from .game_snapshot_inspector import GameSnapshotInspector
from .define_state import PLAYER_STATE
from ..mapper import Mapper
from abc import ABC, abstractmethod
from typing import List

class Bot(ABC):
    """
    Abstract base class representing a bot in a game.

    Attributes:
        side (TeamSide): The side to which the bot belongs.
        number (int): The player number in its team
        init_position (Point): The initial position of the bot.
        mapper (Mapper): The mapper associated with the bot.

    Methods:
        on_disputing(order_set: OrderSet, game_snapshot: GameSnapshot) -> OrderSet: Method called when the player is on DISPUTING_THE_BALL state
        on_defending(order_set: OrderSet, game_snapshot: GameSnapshot) -> OrderSet: Method called when the player is on DEFENDING state
        on_holding(order_set: OrderSet, game_snapshot: GameSnapshot) -> OrderSet: Method called when the player is on HOLDING_THE_BALL state
        on_supporting(order_set: OrderSet, game_snapshot: GameSnapshot) -> OrderSet: Method called when the player is on SUPPORTING state
        as_goalkeeper(order_set: OrderSet, game_snapshot: GameSnapshot, state: PLAYER_STATE) -> OrderSet: Method is called on every turn, and the player state is passed at the last parameter.
        getting_ready(game_snapshot: GameSnapshot): Abstract method for bot preparation before the game.

    Usage:
    Define a subclass of Bot and implement the abstract methods for specific bot behaviors.
    """
    def __init__(self, side: Team.Side, number: int, init_position: Point, my_mapper: Mapper):
        self.number = number
        self.side = side
        self.mapper = my_mapper
        self.initPosition = init_position

    @abstractmethod
    def on_disputing(self, inspector: GameSnapshotInspector) -> List[Order]:
        """
        Method called when the player is on DISPUTING_THE_BALL state.

        Args:
            order_set (OrderSet): The current set of orders.
            game_snapshot (GameSnapshot): The current game snapshot.

        Returns:
            OrderSet: The updated set of orders.
        """
        pass

    @abstractmethod
    def on_defending(self, inspector: GameSnapshotInspector) -> List[Order]:
        """
        Method called when the player is on DEFENDING state

        Args:
            order_set (OrderSet): The current set of orders.
            game_snapshot (GameSnapshot): The current game snapshot.

        Returns:
            OrderSet: The updated set of orders.
        """
        pass

    @abstractmethod
    def on_holding(self, inspector: GameSnapshotInspector) -> List[Order]:
        """
        Method called when the player is on HOLDING_THE_BALL state

        Args:
            order_set (OrderSet): The current set of orders.
            game_snapshot (GameSnapshot): The current game snapshot.

        Returns:
            OrderSet: The updated set of orders.
        """
        pass

    @abstractmethod
    def on_supporting(self, inspector: GameSnapshotInspector) -> List[Order]:
        """
        Method called when the player is on SUPPORTING state

        Args:
            order_set (OrderSet): The current set of orders.
            game_snapshot (GameSnapshot): The current game snapshot.

        Returns:
            OrderSet: The updated set of orders.
        """
        pass

    @abstractmethod
    def as_goalkeeper(self, inspector: GameSnapshotInspector, state: PLAYER_STATE) -> List[Order]:
        """
        Method is called on every turn, and the player state is passed at the last parameter.

        Args:
            order_set (OrderSet): The current set of orders.
            game_snapshot (GameSnapshot): The current game snapshot.
            state (PLAYER_STATE): The current state of the bot.

        Returns:
            OrderSet: The updated set of orders.
        """
        pass

    @abstractmethod
    def getting_ready(self, inspector: GameSnapshotInspector):
        """
        Method called before the game starts and right after the score is changed

        Args:
            game_snapshot (GameSnapshot): The current game snapshot.
        """
        pass

    # def make_reader(self, game_snapshot: lugo.GameSnapshot) -> Tuple[snapshot.GameSnapshotReader, lugo.Player]:
    #     """
    #     Create a game snapshot reader for the bot's side and retrieve the bot's player information.

    #     Args:
    #         game_snapshot (GameSnapshot): The current game snapshot.

    #     Returns:
    #         snapshot.GameSnapshotReader: The game snapshot reader for the bot's side.
    #         Player: The bot's player information.

    #     Raises:
    #         AttributeError: If the bot is not found in the game snapshot.
    #     """
    #     reader = snapshot.GameSnapshotReader(game_snapshot, self.side)
    #     me = reader.get_player(self.side, self.number)
    #     if me is None:
    #         raise AttributeError("did not find myself in the game")

    #     return reader, me



