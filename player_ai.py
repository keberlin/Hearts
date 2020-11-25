import random
from card import *
from player import *


class AIPlayer(Player):
    def __init__(self, id):
        super().__init__(id, "AI %d" % id)
        self.rounds = []

    def _score(self, cards):
        # Calculate a nominal score for a set of cards in one suit
        score = 0
        a = 0
        l = 13 - len(cards) # The more cards we have the lower the score
        for i, card in enumerate(cards):
            c, s = decode(card)
            a += c - i # Keep an accumulation of card vs position
            score += a * l / (i + 1) # Reduce the score the further into the list of cards we are
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

    def pass_cards(self, cards_dealt, direction):
        def _rule_queen_spades(suits):
            # Pass the Queen of Spades if we have less than 4 Spades
            if CARD_QS in suits[SPADES] and len(suits[SPADES]) < 4:
                return CARD_QS

        def _rule_high_spades(suits):
            # If we have no lower spades then ditch the high ones if less than 4 Spades
            lower = list(filter(lambda x: x < CARD_QS, suits[SPADES]))
            if len(lower) == 0 and 1 < len(suits[SPADES]) < 4:
                return suits[SPADES][-1]

        def _rule_high_except_spades(suits):
            # Calculate a nominal score for each suit
            scores = list(filter(lambda x: x[1] != SPADES, [(self._score(suit), i) for i, suit in enumerate(suits)]))
            print(
                f"clubs: {serialize(suits[CLUBS])}, diamonds: {serialize(suits[DIAMONDS])}, spades: {serialize(suits[SPADES])}, hearts: {serialize(suits[HEARTS])}, scores: {scores}"
            )
            scores.sort()
            score, i = scores[-1]
            return suits[i][-1]

        def _rules():
            yield _rule_queen_spades
            yield _rule_high_spades
            yield _rule_high_except_spades

        ret = []

        while len(ret) < 3:
            for rule in _rules():
                # Separate the cards into suits and counts of cards in each suit
                suits = [list(filter(lambda x: in_suit(x, s), cards_dealt)) for s in range(SUITS_IN_DECK)]
                # Run through the rules..
                card = rule(suits)
                if card is not None:
                    ret.append(card)
                    cards_dealt.remove(card)

        # Pad out with random selection if needbe
        # if len(ret) < 3:
        #    print("WARNING passing random cards!")
        #    print(
        #        "clubs:",
        #        serialize(suits[CLUBS]),
        #        "diamonds:",
        #        serialize(suits[DIAMONDS]),
        #        "spades:",
        #        serialize(suits[SPADES]),
        #        "hearts:",
        #        serialize(suits[HEARTS]),
        #        "counts:",
        #        counts,
        #        "scores:",
        #        scores,
        #    )
        #    ret.append(random.sample(cards_dealt, 3 - len(ret)))

        print("pass_cards:", serialize(ret))

        return ret

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
        cards_passed,
        cards_received,
        direction,
    ):
        if len(playable) == 1:
            return playable[0]

        # Separate the cards into suits and counts of cards in each suit
        suits = [list(filter(lambda x: in_suit(x, s), playable)) for s in range(SUITS_IN_DECK)]
        counts = [len(suit) for suit in suits]

        # print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'counts:',counts)

        # If it's the first hand then play highest club
        if turn == 0 and counts[CLUBS]:
            return suits[CLUBS][-1]

        # If we have cards of the lead suit
        if lead_suit is not None and counts[lead_suit]:
            max_card = max(list(filter(lambda x: in_suit(x, lead_suit), cards_in_turn)))
            if lead_suit == SPADES:
                if CARD_QS in playable and max_card > CARD_QS:
                    return CARD_QS
            # See if we are the last player to play
            if len(cards_in_turn) < 3:
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
                elif not CARD_QS in playable and len(cards_in_turn) < 3:
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

    def played_game(self, points_game, rounds_played):
        if min(points_game) == points_game[0]:
            return

        # We didn't come first!
        for turns_played, cards_dealt, cards_passed, cards_received, direction in rounds_played:
            cards_played = set(cards_dealt)
            if cards_passed:
                cards_played -= set(cards_passed)
            if cards_received:
                cards_played |= set(cards_received)
            cards_played = sorted(list(cards_played))
            print(
                f"dealt: {serialize(sorted(list(cards_dealt)))}, passed: {serialize(cards_passed)}, received: {serialize(cards_received)}, direction: {direction}, played: {serialize(cards_played)}"
            )
            for lead, cards in turns_played:
                print(f"lead: {lead} cards: {serialize(cards)}")
