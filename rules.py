"""Rules for both passing cards and playing cards."""
from card import *


class Rules:
    @classmethod
    def _funcs(cls, names):
        return list([getattr(cls, name) for name in names])

    @classmethod
    def _score(cls, cards, avail=[v for v in range(CARDS_IN_SUIT)]):
        if not cards:
            return -1
        # Calculate a nominal score for a set of cards in one suit
        score = 0
        a = 0
        l = len(avail) - len(cards)  # The more cards we have the lower the score
        for i, card in enumerate(cards):
            c, s = decode(card)
            p, _ = decode(avail[i])
            a += c - p  # Keep an accumulation of card vs position
            score += a * l / (i + 1)  # Reduce the score the further into the list of cards we are
        return score / len(cards)

    @classmethod
    def _highest(cls, cards, wrt):
        highest = None
        for card in cards:
            if card >= wrt:
                break
            highest = card
        return highest

    #
    # List of pass cards rules
    #

    @classmethod
    def _pass_two_clubs(cls, suits):
        # Pass the 2 of Clubs
        if CARD_2C in suits[CLUBS]:
            return CARD_2C

    @classmethod
    def _pass_queen_spades(cls, suits):
        # Pass the Queen of Spades if we have less than 4 Spades
        if CARD_QS in suits[SPADES] and len(suits[SPADES]) < 4:
            return CARD_QS

    @classmethod
    def _pass_high_spades(cls, suits):
        # If we have no lower Spades then ditch the high ones, Ace or King
        lower = list(filter(lambda x: x < CARD_QS, suits[SPADES]))
        if len(lower) == 0 and len(suits[SPADES]):
            return suits[SPADES][-1]

    @classmethod
    def _pass_high_except_spades(cls, suits):
        # Calculate a nominal score for each suit
        scores = list(filter(lambda x: x[1] != SPADES, [(cls._score(suit), i) for i, suit in enumerate(suits)]))
        scores.sort()
        score, i = scores[-1]
        return suits[i][-1]

    # TODO: Rule to pass 3 card suits
    # TODO: Rule to pass 2 card suits
    # TODO: Rule to pass single card suits

    #
    # List of play first turn rules
    #

    @classmethod
    def _play_first_turn_highest_card(cls, suits, suits_avail, playable, cards_in_turn):
        # Play the highest card from the highest scoring suit
        scores = [(cls._score(s[0], s[1]), i) for i, s in enumerate(zip(suits, suits_avail))]
        scores.sort()
        max_i = scores[-1][1]
        return suits[max_i][-1]

    #
    # List of play same suit rules
    #

    @classmethod
    def _play_same_suit_queen_spades(cls, suits, suits_avail, playable, cards_in_turn, lead_suit):
        max_card = max(list(filter(lambda x: in_suit(x, lead_suit), cards_in_turn)))

        if lead_suit == SPADES:
            # If we're playing Spades then try to get rid of the Queen
            if CARD_QS in playable and max_card > CARD_QS:
                return CARD_QS

    @classmethod
    def _play_same_suit_spades(cls, suits, suits_avail, playable, cards_in_turn, lead_suit):
        if lead_suit == SPADES:
            # If we have the Queen of Spades then play the King or Ace if possible
            if CARD_QS in playable:
                if len(list(filter(lambda x: x > CARD_QS, suits[SPADES]))) >= 1:
                    return suits[SPADES][-1]

            # If we are not the last player to lay a card then don't play above the Queen of Spades
            if len(cards_in_turn) < 3:
                card = cls._highest(suits[SPADES], CARD_QS)
                if card is not None:
                    # Play the highest card possible under the Queen of Spades
                    return card

            # If we are the last player to lay a card or don't have any losing cards
            ret = suits[SPADES][-1]
            if ret == CARD_QS:
                # Don't play the queen of spades if possible
                if len(suits[SPADES]) > 1:
                    return suits[SPADES][-2]

    @classmethod
    def _play_same_suit_except_spades(cls, suits, suits_avail, playable, cards_in_turn, lead_suit):
        max_card = max(list(filter(lambda x: in_suit(x, lead_suit), cards_in_turn)))

        # If we are not the last player to lay a card then try to lose the hand
        if len(cards_in_turn) < 3:
            # TODO: Play a higher card if we are in the beginning of the round and have relatively few cards of this suit
            # Try to lose if possible
            card = cls._highest(suits[lead_suit], max_card)
            if card is not None:
                # Play the highest losing card possible
                return card
            # Play the lowest card we have
            return suits[lead_suit][0]

        # If we are the last player to lay a card then play the highest possible
        return suits[lead_suit][-1]

    #
    # List of play lead card rules
    #

    @classmethod
    def _play_lead_card(cls, suits, suits_avail, playable):
        # If we have the queen of spades and other cards that are playable
        if CARD_QS in playable and (len(suits[CLUBS]) or len(suits[DIAMONDS]) or len(suits[HEARTS])):
            # Play the highest card from the highest scoring suit except spades
            scores = list(
                filter(
                    lambda x: x[1] != SPADES,
                    [(cls._score(s[0], s[1]), i) for i, s in enumerate(zip(suits, suits_avail))],
                )
            )
            scores.sort()
            max_i = scores[-1][1]
            return suits[max_i][-1]
        # Play the highest Spade less than the Queen of Spades
        card = cls._highest(suits[SPADES], CARD_QS)
        if card is not None:
            return card
        # Play the lowest card from the lowest scoring suit
        # TODO: Need to 'score' suits based on cards remaining!
        scores = list(
            filter(lambda x: x[0] >= 0, [(cls._score(s[0], s[1]), i) for i, s in enumerate(zip(suits, suits_avail))])
        )
        scores.sort()
        min_i = scores[0][1]
        return suits[min_i][0]

    #
    # List of discard card rules
    #

    @classmethod
    def _discard_queen_spades(cls, suits, suits_avail, playable, cards_in_turn, lead_suit):
        if CARD_QS in playable:
            return CARD_QS

    @classmethod
    def _discard_highest(cls, suits, suits_avail, playable, cards_in_turn, lead_suit):
        # Play the highest card from the highest scoring suit
        scores = list(
            filter(lambda x: x[0] >= 0, [(cls._score(s[0], s[1]), i) for i, s in enumerate(zip(suits, suits_avail))])
        )
        scores.sort()
        max_i = scores[-1][1]
        return suits[max_i][-1]
