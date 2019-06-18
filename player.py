import random
from card import *
from distribution import *


class Player():
    def __init__(self,id=None):
        self.id = id
        self.cards = []
        self.distribution = Distribution()

    def _discard(self,card):
        self.cards.remove(card)
        return card

    def deal(self,cards):
        self.cards += cards
        self.cards.sort()

    def pass_cards(self,direction):
        pass

    def play_turn(self,round,lead_suit,cards,playable):
        pass

    def played_hand(self,cards,points):
        for card in cards:
            self.distribution[card] = -1 # Played


class RandomPlayer(Player):
    def pass_cards(self,direction):
        ret = []
        for i in range(3):
            ret.append(self._discard(random.choice(self.cards)))
        return ret

    def play_turn(self,round,lead_suit,cards,playable):
        return self._discard(random.choice(playable))


class AIPlayer(Player):
    def pass_cards(self, direction):
        suits = [list(filter(lambda x:in_suit(x,s),self.cards)) for s in range(SUITS_IN_DECK)]
        lens = [len(suit) for suit in suits]
        print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'lens:',lens)
        ret = []
        # If we have the queen of spades then maybe pass it
        if CARD_QS in self.cards:
            if lens[SPADES] < 4:
                ret.append(self._discard(CARD_QS))
        # If we have no lower spades then ditch the high ones

        # Pad out with random selection
        for i in range(3-len(ret)):
            ret.append(self._discard(random.choice(self.cards)))
        print('pass_cards:',serialize(ret))
        return ret

    def play_turn(self, round, lead_suit, cards, playable):
        # print(self.id,'play_turn:',serialize(playable))
        if len(playable)==1:
            ret = self._discard(playable[0])
        else:
            ret = self._discard(random.choice(playable))
        return ret
