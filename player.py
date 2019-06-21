import random
from card import *
from distribution import *


class Player():
    def __init__(self,id,name):
        self.id = id
        self.name = name

    def __str__(self):
        return 'Player '+self.name

    def _discard(self,card):
        self.cards.remove(card)
        return card

    def deal(self,cards):
        self.cards = cards.copy()
        self.cards.sort()
        self.suit_played = [0 for i in range(SUITS_IN_DECK)]
        self.suit_hands = [0 for i in range(SUITS_IN_DECK)]

    def pass_cards(self,direction):
        pass

    def receive_cards(self,cards):
        self.cards += cards
        self.cards.sort()

    def play_turn(self,round,lead_suit,cards,playable):
        pass

    def played_hand(self,cards,mine,points):
        for i,card in enumerate(cards):
            _,s = decode(card)
            self.suit_played[s] += 1
            if i==0: self.suit_hands[s] += 1

    def played_game(self,game_points):
        pass
