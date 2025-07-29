from .game_snapshot_inspector import GameSnapshotInspector
from ..protos.server_pb2 import Team

class PlayerState(object):
    """
     Represents various states that a player can be in during a game.

     Attributes:
         SUPPORTING (int): The player does not hold the ball, but the holder is a teammate
         HOLDING_THE_BALL (int): The player is holding the ball.
         DEFENDING (int): The ball holder is an opponent player
         DISPUTING_THE_BALL (int): No one is holding the ball

     Methods:
         None
     """
    SUPPORTING = 0
    HOLDING_THE_BALL = 1
    DEFENDING = 2
    DISPUTING_THE_BALL = 3


PLAYER_STATE = PlayerState()

def define_state(inspector: GameSnapshotInspector, player_number: int, side: Team.Side) -> PLAYER_STATE:
    if not inspector or not inspector.get_ball():
        raise AttributeError(
            'invalid snapshot state - cannot define player state')


    me = inspector.get_me()
    if me is None:
        raise AttributeError(
            'could not find the bot in the snapshot - cannot define player state')

    ball_holder = inspector.get_ball_holder()

    if ball_holder.number == 0:
        return PLAYER_STATE.DISPUTING_THE_BALL

    if ball_holder.team_side == side:
        if ball_holder.number == player_number:
            return PLAYER_STATE.HOLDING_THE_BALL

        return PLAYER_STATE.SUPPORTING

    return PLAYER_STATE.DEFENDING
