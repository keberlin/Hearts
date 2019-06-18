import random
from card import *
from distribution import *


class Player():
    def __init__(self,id):
        self.id = id
        self.cards = []
        self.distribution = Distribution()

    def __str__(self):
        return 'Player '+str(self.id)

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
        def _score(cards):
            # Score cards with higher values meaning higher score
            # If we have all the lowest cards then score is 0
            if not len(cards):
                return 0
            score = 0
            for i,card in enumerate(cards):
                c,s = decode(card)
                if i==0: score += c*c
                elif i!=c: score += c
            score //= len(cards)
            return score

        suits = [list(filter(lambda x:in_suit(x,s),self.cards)) for s in range(SUITS_IN_DECK)]
        counts = [len(suit) for suit in suits]
        scores = [_score(suit) for suit in suits]
        print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'counts:',counts,'scores:',scores)

        ret = []

        # If we have the queen of spades then maybe pass it
        if CARD_QS in self.cards:
            if counts[SPADES] < 4:
                ret.append(self._discard(CARD_QS))
                suits[SPADES].remove(CARD_QS)
                counts[SPADES] -= 1
        # If we have no lower spades then ditch the high ones
        lower = len(list(filter(lambda x:x<CARD_QS,suits[SPADES])))
        if lower==0 and counts[SPADES]:
            for card in suits[SPADES]:
                ret.append(self._discard(card))

        # Go through the highest scoring suits and discard their highest cards
        if scores[CLUBS] >= scores[DIAMONDS] and scores[CLUBS] >= scores[HEARTS]:
            for card in reversed(suits[CLUBS]):
                if len(ret)<3: ret.append(self._discard(card))
        if scores[DIAMONDS] >= scores[HEARTS]:
            for card in reversed(suits[DIAMONDS]):
                if len(ret)<3: ret.append(self._discard(card))
        for card in reversed(suits[HEARTS]):
            if len(ret)<3: ret.append(self._discard(card))

        # Pad out with random selection if needbe
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
