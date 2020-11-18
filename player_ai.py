import random
from card import *
from player import *


class Round:
    def __init__(self):
        self.dealt = None
        self.cards_passed = None
        self.cards_received = None
        self.hands = []


class AIPlayer(Player):
    def __init__(self, id):
        super().__init__(id, "AI %d" % id)
        self.rounds = []

    def _score(self, cards):
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
        score /= len(cards)
        return score

    def _min_index(self, scores, counts):
        min_score = None
        for i, score in enumerate(scores):
            if not counts[i]:
                continue
            if not min_score or score < min_score:
                min_score = score
                min_i = i
        return min_i

    def _max_index(self, scores, counts):
        max_score = None
        for i, score in enumerate(scores):
            if not counts[i]:
                continue
            if not max_score or score > max_score:
                max_score = score
                max_i = i
        return max_i

    def _highest(self, cards, wrt):
        highest = None
        for i, card in enumerate(cards):
            if card > wrt:
                break
            highest = i
        # print('highest:', serialize(cards), serialize(wrt), highest)
        return highest

    def dealt(self, cards_dealt):
        self.rounds.append(Round())
        self.rounds[-1].dealt = cards_dealt

    def pass_cards(self, cards_dealt, direction):
        cards_dealt = cards_dealt.copy()

        suits = [list(filter(lambda x: in_suit(x, s), cards_dealt)) for s in range(SUITS_IN_DECK)]
        counts = [len(suit) for suit in suits]
        scores = [self._score(suit) for suit in suits]
        # print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'counts:',counts,'scores:',scores)

        ret = []

        # If we have no lower spades then ditch the high ones
        lower = list(filter(lambda x: x < CARD_QS, suits[SPADES]))
        if len(lower) == 0 and counts[SPADES]:
            for card in suits[SPADES]:
                ret.append(card)
                cards_dealt.remove(card)
        # If we have the queen of spades then maybe pass it
        if CARD_QS in cards_dealt:
            if counts[SPADES] < 4:
                ret.append(CARD_QS)
                cards_dealt.remove(CARD_QS)

        # Go through the highest scoring suits and discard their highest cards
        iscores = [((i, score)) for i, score in enumerate(scores)]
        iscores.sort(key=lambda x: x[1])
        for iscore in reversed(iscores):
            i = iscore[0]
            if i == SPADES:
                continue
            for card in reversed(suits[i]):
                if len(ret) < 3:
                    ret.append(card)
                    cards_dealt.remove(card)

        # Pad out with random selection if needbe
        if len(ret) < 3:
            print("WARNING passing random cards!")
            print(
                "clubs:",
                serialize(suits[CLUBS]),
                "diamonds:",
                serialize(suits[DIAMONDS]),
                "spades:",
                serialize(suits[SPADES]),
                "hearts:",
                serialize(suits[HEARTS]),
                "counts:",
                counts,
                "scores:",
                scores,
            )
            ret.append(random.sample(cards_dealt, 3 - len(ret)))
        # print('pass_cards:',serialize(ret))

        self.rounds[-1].cards_passed = ret

        return ret

    def receive_cards(self, cards_received):
        self.rounds[-1].cards_received = cards_received

    def play_turn(self, turn, lead_suit, cards, playable, hand_points, game_points):
        if len(playable) == 1:
            return playable[0]

        suits = [list(filter(lambda x: in_suit(x, s), playable)) for s in range(SUITS_IN_DECK)]
        counts = [len(suit) for suit in suits]

        # print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'counts:',counts)

        # If it's the first hand then play highest club
        if turn == 0 and counts[CLUBS]:
            return suits[CLUBS][-1]

        # If we have cards of the lead suit
        if lead_suit is not None and counts[lead_suit]:
            max_card = max(list(filter(lambda x: in_suit(x, lead_suit), cards)))
            if lead_suit == SPADES:
                if CARD_QS in playable and max_card > CARD_QS:
                    return CARD_QS
            # See if we are the last player to play
            if len(cards) < 3:
                # Try to lose if possible
                losing = self._highest(suits[lead_suit], max_card)
                if losing is not None:
                    # Play the highest losing card possible
                    return suits[lead_suit][losing]
            # We don't have any cards lower so play the highest possible
            ret = suits[lead_suit][-1]
            if lead_suit == SPADES:
                # Special case for spades
                if ret == CARD_QS:
                    # Don't play the queen of spades if possible
                    if counts[lead_suit] > 1:
                        ret = suits[SPADES][-2]
                elif not CARD_QS in playable and len(cards) < 3:
                    lower = list(filter(lambda x: x < CARD_QS, suits[SPADES]))
                    if len(lower):
                        ret = lower[-1]
            return ret

        scores = [self._score(suit) for suit in suits]

        # print('scores:',scores)

        # If we are starting this hand
        if lead_suit is None:
            # If we have the queen of spades and other suits that are playable
            if CARD_QS in playable and len(list(filter(None, counts))) > 1:
                # Play the highest card from the highest scoring suit except spades
                scores[SPADES] = -1
                max_index = self._max_index(scores, counts)
                return suits[max_index][-1]
            lower = list(filter(lambda x: x < CARD_QS, suits[SPADES]))
            if len(lower) > 1:
                return lower[-1]
            # Play the lowest card from the lowest scoring suit
            min_index = self._min_index(scores, counts)
            return suits[min_index][0]

        # We need to throw away a card
        if CARD_QS in playable:
            return CARD_QS
        if CARD_KS in playable:
            return CARD_KS
        if CARD_AS in playable:
            return CARD_AS
        max_index = self._max_index(scores, counts)
        return suits[max_index][-1]

    def played_hand(self, cards, mine, points):
        super().played_hand(cards, mine, points)
        self.rounds[-1].hands.append((cards, mine, points))

    def played_game(self, game_points):
        me = game_points[3]
        game_points.sort()
        if game_points.index(me) < 3:
            return
        # We came last!
        print("lost:", game_points)
        for i, round in enumerate(self.rounds):
            print("round %d:" % i)
            round.dealt.sort()
            suits = [list(filter(lambda x: in_suit(x, s), round.dealt)) for s in range(SUITS_IN_DECK)]
            print(
                "dealt clubs:",
                serialize(suits[CLUBS]),
                "diamonds:",
                serialize(suits[DIAMONDS]),
                "spades:",
                serialize(suits[SPADES]),
                "hearts:",
                serialize(suits[HEARTS]),
            )
            if round.cards_passed and round.cards_received:
                round.cards_passed.sort()
                round.cards_received.sort()
                print("passed:", serialize(round.cards_passed))
                print("received:", serialize(round.cards_received))
                played = round.dealt + round.cards_received
                for card in round.cards_passed:
                    played.remove(card)
                played.sort()
                suits = [list(filter(lambda x: in_suit(x, s), played)) for s in range(SUITS_IN_DECK)]
                print(
                    "clubs:",
                    serialize(suits[CLUBS]),
                    "diamonds:",
                    serialize(suits[DIAMONDS]),
                    "spades:",
                    serialize(suits[SPADES]),
                    "hearts:",
                    serialize(suits[HEARTS]),
                )
            for j, hand in enumerate(round.hands):
                print("hand %d" % j, serialize(hand[0]), serialize(hand[1]), hand[2])
