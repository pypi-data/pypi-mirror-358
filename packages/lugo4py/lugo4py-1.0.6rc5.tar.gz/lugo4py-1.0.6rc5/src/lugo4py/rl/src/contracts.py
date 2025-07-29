from typing import Any, Tuple, Protocol, Callable

from ... import Team, Order
from ...protos.rl_assistant_pb2 import PlayersOrders, TurnOutcome
from ...protos.server_pb2 import GameSnapshot


class TrainingController(Protocol):
    def set_environment(self, data: Any) -> None:
        """Resets the game to an initial state, passing any necessary data."""
        pass

    def get_state(self) -> Any:
        """Retrieves the inputs used by the model, e.g., tensors for neural networks."""
        pass

    def update(self, action: Any) -> Tuple[float, bool]:
        """Passes the action picked by the model and returns the reward and done values."""
        pass


class BotTrainer(Protocol):
    def create_new_initial_state(self, data: Any) -> GameSnapshot:
        """Sets up the initial state for each game."""
        pass

    def get_training_state(self, snapshot: GameSnapshot) -> Any:
        """Returns the input values (e.g., sensor data) based on the current game state."""
        pass

    def play(self, game_snapshot: GameSnapshot, action: Any) -> PlayersOrders:
        """Translates the action chosen by the model to game orders."""
        pass

    def evaluate(self, previous_game_snapshot: GameSnapshot, new_game_snapshot: GameSnapshot, turn_outcome: TurnOutcome) -> Tuple[float, bool]:
        """Compares the previous and new game states to determine the reward and whether the game is done."""
        pass


class PlayersOrdersBuilder(Protocol):
    def add_order(self, player_number, team_side: Team.Side, orders: list[Order]) -> "PlayersOrdersBuilder":
        pass

    def set_player_behaviour(self, player_number, team_side: Team.Side, behaviour) -> "PlayersOrdersBuilder":
        pass

    def build(self) -> PlayersOrders:
        pass


TrainingFunction = Callable[[TrainingController], None]


class Config:
    def __init__(self, grpc_address):
        """Configuration for the gRPC server."""
        self.grpc_address = grpc_address


# Constants
BOT_BEHAVIOUR_STATUES = "statues"
BOT_BEHAVIOUR_KIDS = "kids"
BOT_BEHAVIOUR_DEFENSES = "defenses"
