import random
from card import *
from player import *


class AIPlayer(Player):
    def __init__(self, id):
        super().__init__(id, "AI %d" % id)
        self.rounds = []

    def _score(self, cards):
        if not cards:
            return -1
        # Calculate a nominal score for a set of cards in one suit
        score = 0
        a = 0
        l = 13 - len(cards)  # The more cards we have the lower the score
        for i, card in enumerate(cards):
            c, s = decode(card)
            a += c - i  # Keep an accumulation of card vs position
            score += a * l / (i + 1)  # Reduce the score the further into the list of cards we are
        return score / len(cards)

    def _min_index(self, scores, counts):
        min_score = None
        for i, score in enumerate(scores):
            if not counts[i]:
                continue
            if not min_score or score < min_score:
                min_score = score
                min_i = i
        return min_i

    def _highest(self, cards, wrt):
        highest = None
        for card in cards:
            if card > wrt:
                break
            highest = card
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

        # print("pass_cards:", serialize(ret))

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
        def _play_highest_club(suits, playable, cards_in_turn):
            # Play the highest club
            if len(suits[CLUBS]):
                return suits[CLUBS][-1]

        def _rules_first_turn():
            yield _play_highest_club

        def _play_same_suit(suits, playable, cards_in_turn, lead_suit):
            max_card = max(list(filter(lambda x: in_suit(x, lead_suit), cards_in_turn)))

            if lead_suit == SPADES:
                # If we're playing Spades then try to get rid of the Queen
                if CARD_QS in playable and max_card > CARD_QS:
                    return CARD_QS

                # If we are not the last player to lay a card then don't play above the Queen of Spades
                if len(cards_in_turn) < 3:
                    losing = self._highest(suits[lead_suit], CARD_QS)
                    if losing is not None:
                        # Play the highest card possible under the Queen of Spades
                        return losing

                # If we are the last player to lay a card or don't have any losing cards
                ret = suits[lead_suit][-1]
                if ret == CARD_QS:
                    # Don't play the queen of spades if possible
                    if len(suits[SPADES]) > 1:
                        return suits[SPADES][-2]

            # If we are not the last player to lay a card then try to lose the hand
            if len(cards_in_turn) < 3:
                # Try to lose if possible
                losing = self._highest(suits[lead_suit], max_card)
                if losing is not None:
                    # Play the highest losing card possible
                    return losing
                # Play the lowest card we have
                return suits[lead_suit][0]

            # If we are the last player to lay a card then play the highest possible
            return suits[lead_suit][-1]

        def _rules_play_same_suit():
            yield _play_same_suit

        def _play_lead_card(suits, playable):
            # If we have the queen of spades and other cards that are playable
            if CARD_QS in playable and (len(suits[CLUBS]) or len(suits[DIAMONDS]) or len(suits[HEARTS])):
                # Play the highest card from the highest scoring suit except spades
                scores = list(
                    filter(lambda x: x[1] != SPADES, [(self._score(suit), i) for i, suit in enumerate(suits)])
                )
                scores.sort()
                max_i = scores[-1][1]
                return suits[max_i][-1]
            lower = list(filter(lambda x: x < CARD_QS, suits[SPADES]))
            if len(lower) > 1:
                return lower[-1]
            # Play the lowest card from the lowest scoring suit
            scores = list(filter(lambda x: x[0] >= 0, [(self._score(suit), i) for i, suit in enumerate(suits)]))
            scores.sort()
            min_i = scores[0][1]
            return suits[min_i][0]

        def _rules_play_lead_card():
            yield _play_lead_card

        def _discard_queen_spades(suits, playable, cards_in_turn, lead_suit):
            if CARD_QS in playable:
                return CARD_QS

        def _discard_highest(suits, playable, cards_in_turn, lead_suit):
            # Play the highest card from the highest scoring suit
            scores = list(filter(lambda x: x[0] >= 0, [(self._score(suit), i) for i, suit in enumerate(suits)]))
            scores.sort()
            max_i = scores[-1][1]
            return suits[max_i][-1]

        def _rules_discard():
            yield _discard_queen_spades
            yield _discard_highest

        # If only one card is playable then Hobson's choice
        if len(playable) == 1:
            return playable[0]

        # Separate the cards into suits and counts of cards in each suit
        suits = [list(filter(lambda x: in_suit(x, s), playable)) for s in range(SUITS_IN_DECK)]

        # print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'counts:',counts)

        # If it's the first card to be played
        if turn == 0:
            for rule in _rules_first_turn():
                ret = rule(suits, playable, cards_in_turn)
                if ret is not None:
                    return ret

        # If we have cards of the lead suit we need to choose one of the same suit
        if lead_suit is not None and len(suits[lead_suit]):
            for rule in _rules_play_same_suit():
                ret = rule(suits, playable, cards_in_turn, lead_suit)
                if ret is not None:
                    return ret

        # If we are starting this hand and the first to play a card
        if lead_suit is None:
            for rule in _rules_play_lead_card():
                ret = rule(suits, playable)
                if ret is not None:
                    return ret

        # We need to throw away a card
        for rule in _rules_discard():
            ret = rule(suits, playable, cards_in_turn, lead_suit)
            if ret is not None:
                return ret

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
                f"dealt: {serialize(sorted(list(cards_dealt)))}, passed: {serialize(cards_passed)}, received: {serialize(cards_received)}, direction: {direction}, hand played: {serialize(cards_played)}"
            )
            for lead, cards, points in turns_played:
                print(f"lead: {lead} cards: {serialize(cards)}, points: {points[0]}")
