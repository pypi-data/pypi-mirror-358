from ..protos import server_pb2
from ..mapper import DIRECTION, ORIENTATION, homeGoal, awayGoal

from . import geo, helpers, specs
from ..protos.physics_pb2 import Point, Vector
from ..protos.server_pb2 import Team, GameSnapshot, Player


# Assuming that Lugo, Geo, Helpers, and other dependencies are defined elsewhere

class GameSnapshotInspector:
    def __init__(self, bot_side: Team.Side, player_number: int, game_snapshot: GameSnapshot):
        self.my_side = bot_side
        self.my_number = player_number
        self.snapshot = game_snapshot
        self.me = self.get_player(bot_side, player_number)
        if not self.me:
            raise ValueError(f"Could not find the player {bot_side}-{player_number}")

    def get_snapshot(self):
        return self.snapshot

    def get_turn(self):
        return self.snapshot.turn

    def get_me(self):
        return self.me

    def get_ball(self):
        return self.snapshot.ball if self.snapshot else None

    def get_player(self, side: Team.Side, number: int):
        return helpers.get_player(self.snapshot, side, number)

    def get_ball_holder(self):
        return helpers.get_ball_holder(self.snapshot)

    def is_ball_holder(self, player: Player):
        return helpers.is_ball_holder(self.snapshot, player)

    def get_team(self, side: Team.Side):
        return helpers.get_team(self.snapshot, side)

    def get_my_team(self):
        return self.get_team(self.my_side)

    def get_opponent_team(self):
        return self.get_team(self.get_opponent_side())

    def get_my_team_side(self):
        return self.my_side

    def get_opponent_side(self):
        return helpers.get_opponent_side(self.my_side)

    def get_my_team_players(self):
        my_team = self.get_my_team()
        return my_team.players if my_team else []

    def get_opponent_players(self):
        opponent_team = self.get_opponent_team()
        return opponent_team.players if opponent_team else []

    def get_my_team_goalkeeper(self):
        return self.get_player(self.get_my_team_side(), specs.GOALKEEPER_NUMBER)

    def get_opponent_goalkeeper(self):
        return self.get_player(self.get_opponent_side(), specs.GOALKEEPER_NUMBER)

    # ###############

    def make_order_move(self, target: Point, speed: int):
        return self.make_order_move_from_point(self.me.position if self.me else geo.new_zeroed_point(), target, speed)

    def make_order_move_max_speed(self, target: Point):
        return self.make_order_move_from_point(self.me.position if self.me else geo.new_zeroed_point(), target, specs.PLAYER_MAX_SPEED)

    def make_order_move_from_point(self, origin: Point, target: Point, speed: int):
        direction = geo.new_vector(origin, target)
        normalizedDirection = geo.normalize(direction)

        order = server_pb2.Order()
        order.move.velocity.direction.CopyFrom(normalizedDirection)
        order.move.velocity.speed = speed
        return order

    def make_order_move_from_vector(self, direction: Vector, speed: int):
        target_point = geo.target_from(direction, self.me.position if self.me else geo.new_zeroed_point())
        return self.make_order_move_from_point(self.me.position if self.me else geo.new_zeroed_point(), target_point, speed)

    def make_order_move_by_direction(self, direction, speed=None):
        direction_target = self.get_orientation_by_direction(direction, self.my_side)
        return self.make_order_move_from_vector(direction_target, speed if speed is not None else specs.PLAYER_MAX_SPEED)

    def make_order_move_to_stop(self):
        my_direction = self.me.velocity.direction if self.me and self.me.velocity else self.get_orientation_by_direction(DIRECTION.FORWARD)
        return self.make_order_move_from_vector(my_direction, 0)

    def make_order_jump(self, target, speed):
        direction = geo.new_vector(self.me.position if self.me else geo.new_zeroed_point(), target)
        normalizedDirection = geo.normalize(direction)

        order = server_pb2.Order()
        order.jump.velocity.direction.CopyFrom(normalizedDirection)
        order.jump.velocity.speed = speed
        return order

    def make_order_kick(self, target: Point, speed: int):
        ball_expected_direction = geo.new_vector(self.get_ball().position if self.snapshot and self.get_ball() else geo.new_zeroed_point(), target)
        diff_vector = geo.sub_vector(ball_expected_direction, self.get_ball().velocity.direction if self.snapshot and self.get_ball() and self.get_ball().velocity else geo.new_zeroed_point())
        normalizedDirection = geo.normalize(diff_vector)

        order = server_pb2.Order()
        order.kick.velocity.direction.CopyFrom(normalizedDirection)
        order.kick.velocity.speed = speed
        return order

    def make_order_kick_max_speed(self, target: Point):
        return self.make_order_kick(target, specs.BALL_MAX_SPEED)

    def make_order_catch(self):
        order = server_pb2.Order()
        order.catch.SetInParent()
        return order

    def get_orientation_by_direction(self, direction: DIRECTION, my_side: Team.Side):
        if direction == DIRECTION.FORWARD:
            return ORIENTATION.EAST if my_side == Team.Side.HOME else ORIENTATION.WEST
        elif direction == DIRECTION.BACKWARD:
            return ORIENTATION.WEST if my_side == Team.Side.HOME else ORIENTATION.EAST
        elif direction == DIRECTION.LEFT:
            return ORIENTATION.NORTH if my_side == Team.Side.HOME else ORIENTATION.SOUTH
        elif direction == DIRECTION.RIGHT:
            return ORIENTATION.SOUTH if my_side == Team.Side.HOME else ORIENTATION.NORTH
        elif direction == DIRECTION.BACKWARD_LEFT:
            return ORIENTATION.NORTH_WEST if my_side == Team.Side.HOME else ORIENTATION.SOUTH_EAST
        elif direction == DIRECTION.BACKWARD_RIGHT:
            return ORIENTATION.SOUTH_WEST if my_side == Team.Side.HOME else ORIENTATION.NORTH_EAST
        elif direction == DIRECTION.FORWARD_LEFT:
            return ORIENTATION.NORTH_EAST if my_side == Team.Side.HOME else ORIENTATION.SOUTH_WEST
        elif direction == DIRECTION.FORWARD_RIGHT:
            return ORIENTATION.SOUTH_EAST if my_side == Team.Side.HOME else ORIENTATION.NORTH_WEST
        else:
            raise ValueError(f"Unknown direction {direction}")