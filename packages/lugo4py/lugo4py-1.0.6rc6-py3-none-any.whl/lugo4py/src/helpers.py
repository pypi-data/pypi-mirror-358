from ..protos.server_pb2 import GameSnapshot, Player, Team


def get_ball_holder(snapshot: GameSnapshot):
    holder = snapshot.ball.holder
    return holder if holder is not None else None

def is_ball_holder(snapshot: GameSnapshot, player: Player):
    holder = snapshot.ball.holder
    return holder is not None and holder.team_side == player.team_side and holder.number == player.number

def get_team(snapshot: GameSnapshot, side: Team.Side):
    if side == Team.Side.HOME:
        return snapshot.home_team
    else: return snapshot.away_team


def get_player(snapshot: GameSnapshot, side: Team.Side, number: int):
    team = get_team(snapshot, side)
    if team:
        for current_player in team.players:
            if current_player.number == number:
                return current_player
    return None

def get_opponent_side(side: Team.Side):
    return Team.Side.AWAY if side == Team.Side.HOME else Team.Side.HOME


