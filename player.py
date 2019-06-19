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

    def played_hand(self,cards,hand_points,player_points):
        for card in cards:
            _,s = decode(card)
            self.remaining[s] -= 1


class RandomPlayer(Player):
    def __init__(self,id):
        super().__init__(id,'Random %d'%id)

    def pass_cards(self,direction):
        ret = []
        for i in range(3):
            ret.append(self._discard(random.choice(self.cards)))
        return ret

    def play_turn(self,round,lead_suit,cards,playable, hand_points, player_points):
        return self._discard(random.choice(playable))


class AIPlayer(Player):
    def __init__(self, id):
        super().__init__(id, 'AI %d' % id)

    def _score(self,cards):
        # Score cards with higher values meaning higher score
        # If we have all the lowest cards then score is 0
        if not len(cards):
            return 0
        score = 0
        for i, card in enumerate(cards):
            c, s = decode(card)
            if i == 0:
                score += c * c
            elif i != c:
                score += c
        score //= len(cards)
        return score

    def _min_index(self,scores,counts):
        min_score = None
        for i,score in enumerate(scores):
            if not counts[i]: continue
            if not min_score or score<min_score:
                min_score = score
                min_i = i
        return min_i

    def _max_index(self,scores,counts):
        max_score = None
        for i,score in enumerate(scores):
            if not counts[i]: continue
            if not max_score or score<max_score:
                max_score = score
                max_i = i
        return max_i

    def pass_cards(self, direction):
        suits = [list(filter(lambda x:in_suit(x,s),self.cards)) for s in range(SUITS_IN_DECK)]
        counts = [len(suit) for suit in suits]
        scores = [self._score(suit) for suit in suits]
        print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'counts:',counts,'scores:',scores)

        ret = []

        # If we have no lower spades then ditch the high ones
        lower = list(filter(lambda x:x<CARD_QS,suits[SPADES]))
        if len(lower)==0 and counts[SPADES]:
            for card in suits[SPADES]:
                ret.append(self._discard(card))
        # If we have the queen of spades then maybe pass it
        if CARD_QS in self.cards:
            if counts[SPADES] < 4:
                ret.append(self._discard(CARD_QS))

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

    def play_turn(self, hand, lead_suit, cards, playable, hand_points, player_points):
        if len(playable)==1:
            return self._discard(playable[0])

        suits = [list(filter(lambda x:in_suit(x,s),playable)) for s in range(SUITS_IN_DECK)]
        counts = [len(suit) for suit in suits]

        # If it's the first hand then ditch highest club
        if hand==0 and counts[CLUBS]:
            return self._discard(suits[CLUBS][-1])

        # If we have cards of the lead suit
        if lead_suit and counts[lead_suit]:
            max_card = max(cards)
            for i,card in enumerate(suits[lead_suit]):
                if card > max_card:
                    break
            if i==0:
                # We don't have any cards lower so play the highest
                return self._discard(suits[lead_suit][-1])
            # Play the highest card possible
            return self._discard(suits[lead_suit][i-1])

        scores = [self._score(suit) for suit in suits]

        # If we are starting this hand
        if not lead_suit:
            if CARD_QS in playable:
                # Play the highest card from the highest scoring suit except spades
                scores[SPADES] = -1
                max_index = self._max_index(scores,counts)
                return self._discard(suits[max_index][-1])
            lower = list(filter(lambda x: x < CARD_QS, suits[SPADES]))
            if len(lower)>1:
                return self._discard(lower[-1])
            # Play the lowest card from the lowest scoring suit
            min_index = self._min_index(scores,counts)
            print('scores:',scores,'min_index:',min_index)
            return self._discard(suits[min_index][0])

        # We need to ditch a card
        if CARD_QS in playable: return self._discard(CARD_QS)
        if CARD_KS in playable: return self._discard(CARD_KS)
        if CARD_AS in playable: return self._discard(CARD_AS)
        max_index = self._max_index(scores,counts)
        print('scores:',scores,'max_index:',max_index)
        return self._discard(suits[max_index][-1])
