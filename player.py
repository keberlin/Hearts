import random
from card import *
from distribution import *


class Player():
    def __init__(self,id,name):
        self.id = id
        self.name = name

    def __str__(self):
        return 'Player '+self.name

    def reset(self):
        self.cards = []
        self.remaining = [CARDS_IN_SUIT for i in range(SUITS_IN_DECK)]

    def _discard(self,card):
        self.cards.remove(card)
        return card

    def deal(self,cards):
        self.cards += cards
        self.cards.sort()

    def pass_cards(self,direction):
        pass

    def receive_cards(self,cards):
        self.cards += cards
        self.cards.sort()

    def play_turn(self,round,lead_suit,cards,playable):
        pass

    def played_hand(self,cards,mine):
        for card in cards:
            _,s = decode(card)
            self.remaining[s] -= 1

    def played_game(self,game_points):
        pass
