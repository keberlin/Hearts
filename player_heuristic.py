import random

from sqlalchemy import and_, or_

from card import *
from database import db_init, HEARTS_DB_URI
from model import GameModel, HandModel, PassingModel, PlayerModel
from player import Player

session = db_init(HEARTS_DB_URI)


class HeuristicPlayer(Player):
    def __init__(self, id):
        super().__init__(id, "Heuristic")
        self.number_of_passing = 0
        self.number_of_passing_hits = 0
        self.number_of_turns = 0
        self.number_of_turns_hits = 0

    def pass_cards(self, cards_dealt, direction):
        self.number_of_passing += 1
        results = (
            session.query(PassingModel)
            .filter(PassingModel.dealt == serializedb(cards_dealt, sort=True), PassingModel.direction == direction)
            .order_by(PassingModel.points)
            .first()
        )
        if results:
            self.number_of_passing_hits += 1
            return deserializedb(results.passed)
        return random.sample(cards_dealt, 3)

    def play_turn(
        self,
        turn,
        lead_suit,
        cards_in_turn,
        hand,
        playable,
        points_round,
        points_game,
        turns_played,
        cards_remaining,
        cards_dealt,
        direction,
        cards_passed,
        cards_received,
        cards_playing,
    ):
        self.number_of_turns += 1
        # TODO: Need to add turns..
        results = (
            session.query(HandModel)
            .filter(HandModel.playing == serializedb(cards_playing, sort=True))
            .order_by(HandModel.points)
            .first()
        )
        if results:
            self.number_of_turns_hits += 1
            return deserializedb(results.turns[n : n + 1])
        return random.choice(playable)

    def played_game(self, points_game, hands_played):
        print(f"passing %: {self.number_of_passing_hits*100/self.number_of_passing:.2f}")
        print(f"hands %: {self.number_of_turns_hits*100/self.number_of_turns:.2f}")
