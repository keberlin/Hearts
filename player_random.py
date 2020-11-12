import random
from player import *


class RandomPlayer(Player):
    def __init__(self, id):
        super().__init__(id, "Random %d" % id)

    def pass_cards(self, cards_dealt, direction):
        return random.sample(cards_dealt, 3)

    def receive_cards(self, cards_received):
        pass

    def play_turn(self, turn, lead_suit, cards, playable, hand_points, player_points):
        return random.choice(playable)
