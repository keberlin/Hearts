from player import *

class AIPlayer(Player):
    def __init__(self, id):
        super().__init__(id, 'AI %d' % id)

    def reset(self):
        super().reset()
        self.dealt = None
        self.passed_cards = None
        self.received_cards = None
        self.hands = []

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

    def deal(self,cards):
        super().deal(cards)
        self.dealt = cards.copy()

    def pass_cards(self, direction):
        suits = [list(filter(lambda x:in_suit(x,s),self.cards)) for s in range(SUITS_IN_DECK)]
        counts = [len(suit) for suit in suits]
        scores = [self._score(suit) for suit in suits]
        #print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'counts:',counts,'scores:',scores)

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
        #print('pass_cards:',serialize(ret))
        self.passed_cards = ret
        return ret

    def receive_cards(self,cards):
        super().receive_cards(cards)
        self.received_cards = cards

    def play_turn(self, hand, lead_suit, cards, playable, hand_points, game_points):
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
            return self._discard(suits[min_index][0])

        # We need to ditch a card
        if CARD_QS in playable: return self._discard(CARD_QS)
        if CARD_KS in playable: return self._discard(CARD_KS)
        if CARD_AS in playable: return self._discard(CARD_AS)
        max_index = self._max_index(scores,counts)
        return self._discard(suits[max_index][-1])

    def played_hand(self,cards,mine):
        super().played_hand(cards,mine)
        self.hands.append((cards,mine))

    def played_game(self,game_points):
        me = game_points[3]
        game_points.sort()
        if game_points.index(me) < 3:
            return
        # We came last!
        print('lost:',game_points)
        self.dealt.sort()
        suits = [list(filter(lambda x:in_suit(x,s),self.dealt)) for s in range(SUITS_IN_DECK)]
        print('dealt clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]))
        if self.passed_cards and self.received_cards:
            self.passed_cards.sort()
            self.received_cards.sort()
            print('passed:',serialize(self.passed_cards))
            print('received:',serialize(self.received_cards))
            played = self.dealt+self.received_cards
            for card in self.passed_cards: played.remove(card)
            played.sort()
            suits = [list(filter(lambda x:in_suit(x,s),played)) for s in range(SUITS_IN_DECK)]
            print('played clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]))
        for i,hand in enumerate(self.hands):
            print('hand %d'%i,serialize(hand[0]),serialize(hand[1]))
