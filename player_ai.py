from player import *


class Round():
    def __init__(self):
        self.dealt = None
        self.passed_cards = None
        self.received_cards = None
        self.hands = []


class AIPlayer(Player):
    def __init__(self, id):
        super().__init__(id, 'AI %d' % id)
        self.rounds = []

    def round(self):
        super().round()
        self.rounds.append(Round())

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

    def _highest(self,cards,wrt):
        highest = None
        for i, card in enumerate(cards):
            if card > wrt:
                break
            highest = i
        #print('highest:', serialize(cards), serialize(wrt), highest)
        return highest

    def deal(self,cards):
        super().deal(cards)
        self.rounds[-1].dealt = cards

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
        self.rounds[-1].passed_cards = ret
        return ret

    def receive_cards(self,cards):
        super().receive_cards(cards)
        self.rounds[-1].received_cards = cards

    def play_turn(self, hand, lead_suit, cards, playable, hand_points, game_points):
        if len(playable)==1:
            return self._discard(playable[0])

        suits = [list(filter(lambda x:in_suit(x,s),playable)) for s in range(SUITS_IN_DECK)]
        counts = [len(suit) for suit in suits]

        # If it's the first hand then play highest club
        if hand==0 and counts[CLUBS]:
            return self._discard(suits[CLUBS][-1])

        # If we have cards of the lead suit
        if lead_suit and counts[lead_suit]:
            max_card = max(list(filter(lambda x:in_suit(x,lead_suit),cards)))
            highest = self._highest(suits[lead_suit],max_card)
            if not highest:
                # We don't have any cards lower so play the highest possible
                ret = suits[lead_suit][-1]
                if lead_suit==SPADES:
                    # Special case for spades
                    if ret==CARD_QS:
                        # Don't play the queen of spades if possible
                        if counts[lead_suit]>1:
                            ret = suits[lead_suit][-2]
                    elif not CARD_QS in playable:
                        lower = list(filter(lambda x: x < CARD_QS, suits[SPADES]))
                        if len(lower):
                            ret = lower[-1]
                return self._discard(ret)
            # Play the highest card possible
            return self._discard(suits[lead_suit][highest])

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

    def played_hand(self,cards,mine,points):
        super().played_hand(cards,mine,points)
        self.rounds[-1].hands.append((cards,mine,points))

    def played_game(self,game_points):
        me = game_points[3]
        game_points.sort()
        if game_points.index(me) < 3:
            return
        # We came last!
        print('lost:',game_points)
        for i,round in enumerate(self.rounds):
            print('round %d:'%i)
            round.dealt.sort()
            suits = [list(filter(lambda x:in_suit(x,s),round.dealt)) for s in range(SUITS_IN_DECK)]
            print('dealt clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]))
            if round.passed_cards and round.received_cards:
                round.passed_cards.sort()
                round.received_cards.sort()
                print('passed:',serialize(round.passed_cards))
                print('received:',serialize(round.received_cards))
                played = round.dealt+round.received_cards
                for card in round.passed_cards: played.remove(card)
                played.sort()
                suits = [list(filter(lambda x:in_suit(x,s),played)) for s in range(SUITS_IN_DECK)]
                print('played clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]))
            for j,hand in enumerate(round.hands):
                print('hand %d'%j,serialize(hand[0]),serialize(hand[1]),hand[2])

