import random

from player import *


class RandomPlayer(Player):
    def __init__(self, id):
        super().__init__(id, "Random %d" % id)

    def pass_cards(self, cards_dealt, direction):
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
    ):
        return random.choice(playable)
