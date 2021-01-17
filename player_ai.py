import random
import re

from player import *
from rules import *

NUM_PLAYERS = 4


class AIPlayer(Player):
    def __init__(self, id):
        def _func_names(prefix):
            names = list(filter(lambda f: re.match(prefix, f), dir(Rules)))
            names = random.sample(names, random.randint(1, len(names)))
            random.shuffle(names)
            return names

        # Get a list of supported rules for passing and playing cards
        self.rules_pass = _func_names("_pass")
        self.rules_play_first_turn = _func_names("_play_first_turn")
        self.rules_play_same_suit = _func_names("_play_same_suit")
        self.rules_play_lead_card = _func_names("_play_lead_card")
        self.rules_discard = _func_names("_discard")
        rules = (
            self.rules_pass
            + self.rules_play_first_turn
            + self.rules_play_same_suit
            + self.rules_play_lead_card
            + self.rules_discard
        )
        funcs = ",".join(rules)
        super().__init__(id, f"AI: {funcs}")

        self.rounds = []

    @classmethod
    def _current_winner(cls, cards_in_turn):
        if len(cards_in_turn) < 1:
            return None
        _, lead_suit = decode(cards_in_turn[0])
        max_card = max(list(filter(lambda x: in_suit(x, lead_suit), cards_in_turn)))
        return cards_in_turn.index(max_card)

    @classmethod
    def _suits_depleted(cls, turns_played):
        suits_depleted = [[False] * SUITS_IN_DECK] * NUM_PLAYERS
        for lead, cards_played in turns_played:
            for i, card in enumerate(cards_played):
                _, s = decode(card)
                if i == 0:
                    lead_suit = s
                elif s != lead_suit:
                    suits_depleted[(lead - i) % NUM_PLAYERS][s] = True
        # TODO: If a player plays a Heart card before Hearts have broken then he must be out of the other suits
        return suits_depleted

    #
    # Game contract for passing cards
    #
    def pass_cards(self, cards_dealt, direction):

        print(serialize(cards_dealt))

        ret = []

        for i in range(3):
            for rule in Rules._funcs(self.rules_pass):
                # Separate the cards into suits
                suits = split_into_suits(cards_dealt)
                # Run through the rules..
                card = rule(suits)
                if card is not None:
                    ret.append(card)
                    cards_dealt.remove(card)
                    break

        # Pad out with random selection as a last resort
        if len(ret) < 3:
            ret.extend(random.sample(cards_dealt, 3 - len(ret)))

        # print("pass_cards:", serialize(ret))

        return ret

    #
    # Game contract for playing a turn
    #
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
        FACT_HEARTS_BROKEN = 0
        FACT_HEARTS_IN_THIS_TURN = 1
        FACT_QS_ALREADY_PLAYED = 2
        FACT_QS_IN_THIS_TURN = 3
        FACT_STILL_HAVE_QS = 4
        FACT_REMAINING_PLAYER_WITH_QS = 5
        FACT_POSSIBLE_SHOOT_THE_MOON = 6
        NUM_OF_FACTS = 7

        # If only one card is playable then Hobson's choice
        if len(playable) == 1:
            return playable[0]

        # Separate the cards into suits and score each one
        suits = split_into_suits(playable)
        suits_avail = split_into_suits(cards_remaining)

        # Determine facts about cards in each suit:
        # Are there any cards left in play for each suit?
        suits_remaining = split_into_suits(cards_remaining - set(hand) - set(cards_in_turn))
        # Are any of the remaining players out of cards from the lead suit?
        suits_depleted = self._suits_depleted(turns_played)

        # Determine facts about this round:
        facts = [False] * NUM_OF_FACTS
        # Has hearts been broken? Ie have any Hearts been played in previous turns.
        facts[FACT_HEARTS_BROKEN] = len(list(filter(lambda x: in_suit(x, HEARTS), set(DECK) - cards_remaining))) > 0
        # Have any Hearts been played in this turn?
        facts[FACT_HEARTS_IN_THIS_TURN] = len(list(filter(lambda x: in_suit(x, HEARTS), cards_in_turn))) > 0
        # Has the Queen of Spades been played in previous turns?
        facts[FACT_QS_ALREADY_PLAYED] = CARD_QS in (set(DECK) - (cards_remaining | set(cards_in_turn)))
        # Has the Queen of Spades been played in this turn?
        facts[FACT_QS_IN_THIS_TURN] = CARD_QS in cards_in_turn
        # Do we still hold the Queen of Spades?
        facts[FACT_STILL_HAVE_QS] = CARD_QS in hand
        # Do any of the remaining players have the Queen of Spades?
        # Ie it's not been played yet and we passed it to a player or we know that only one player has Spades left and that player is yet to play
        passed_to = 1 if direction == 0 else 3 if direction == 1 else 2 if direction == 2 else None
        facts[FACT_REMAINING_PLAYER_WITH_QS] = (
            not facts[FACT_QS_ALREADY_PLAYED] and not facts[FACT_QS_IN_THIS_TURN]
        ) and (cards_passed is not None and CARD_QS in cards_passed and len(cards_in_turn) <= 3 - passed_to)
        # Is there a chance of shooting the moon?
        # Ie only one player with points this round and is currently winning this hand with points.
        current_winner = self._current_winner(cards_in_turn)
        facts[FACT_POSSIBLE_SHOOT_THE_MOON] = (
            len(list(filter(None, points_round))) == 1
            and (current_winner and points_round[current_winner])
            and (facts[FACT_HEARTS_IN_THIS_TURN] or facts[FACT_QS_IN_THIS_TURN])
        )

        # print('clubs:',serialize(suits[CLUBS]),'diamonds:',serialize(suits[DIAMONDS]),'spades:',serialize(suits[SPADES]),'hearts:',serialize(suits[HEARTS]),'counts:',counts)

        # If it's the first turn then choose a card bearing in mind we can't receive any points
        if turn == 0:
            for rule in Rules._funcs(self.rules_play_first_turn):
                ret = rule(suits, suits_avail, playable, cards_in_turn)
                if ret is not None:
                    return ret

        # If we have cards of the lead suit we need to choose one of them
        if lead_suit is not None and len(suits[lead_suit]):
            for rule in Rules._funcs(self.rules_play_same_suit):
                ret = rule(suits, suits_avail, playable, cards_in_turn, lead_suit)
                if ret is not None:
                    return ret

        # If we are starting this hand we need to choose a card to play
        if lead_suit is None:
            for rule in Rules._funcs(self.rules_play_lead_card):
                ret = rule(suits, suits_avail, playable)
                if ret is not None:
                    return ret

        # If we have no cards in the lead suit then we need to discard a card
        for rule in Rules._funcs(self.rules_discard):
            ret = rule(suits, suits_avail, playable, cards_in_turn, lead_suit)
            if ret is not None:
                return ret

        # Play a random card as a last resort
        return random.choice(playable)

    #
    # Game contract offering analysis of a played game
    #
    def played_game(self, points_game, rounds_played):
        if min(points_game) == points_game[0]:
            return

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
