import random
from statistics import mean

from sqlalchemy import and_, or_

from card import *
from database import db_init, HEARTS_DB_URI
from logger import logger
from model import GameModel, HandModel, PassingModel, PlayerModel
from player import Player

session = db_init(HEARTS_DB_URI)


def _turndb(pos: int, cards: list):
    return f"{pos} {serializedb(cards)}"


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
            .all()
        )
        if results:
            self.number_of_passing_hits += 1
            points = {}
            for result in results:
                if result.passed not in points:
                    points[result.passed] = []
                points[result.passed].append(result.points)
            print(f"points: {points}")
            scores = []
            for k, v in points.items():
                scores.append((k, mean(v)))
            scores.sort(key=lambda x: x[1])
            print(f"scores: {scores}")
            passed = scores[0][0]
            print(
                f"dealt: {serializepr(cards_dealt, sort=True)}, direction: {direction}, pass: {serializepr(deserializedb(passed))}"
            )
            logger.info(
                f"dealt: {serializepr(cards_dealt, sort=True)}, direction: {direction}, pass: {serializepr(deserializedb(passed))}"
            )
            return deserializedb(passed)
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
        pos = len(cards_in_turn)
        turns = " ".join([_turndb(v[0], v[1]) for v in turns_played + [(pos, cards_in_turn)]])
        results = (
            session.query(HandModel.turns)
            .filter(HandModel.playing == serializedb(cards_playing, sort=True))
            .filter(HandModel.turns.startswith(turns))
            .order_by(HandModel.points)
            .first()
        )
        if results:
            self.number_of_turns_hits += 1
            n = len(turns)
            logger.info(
                f"playing: {serializepr(cards_playing, sort=True)}, turns: {turns}, play: {results.turns[n:n+2]}"
            )
            return deserialize(results.turns[n : n + 2])
        return random.choice(playable)

    def played_game(self, points_game, hands_played):
        if self.number_of_passing_hits:
            logger.info(f"passing: {self.number_of_passing_hits*100/self.number_of_passing:.1f}%")
        if self.number_of_turns_hits:
            logger.info(f"turns: {self.number_of_turns_hits*100/self.number_of_turns:.1f}%")
