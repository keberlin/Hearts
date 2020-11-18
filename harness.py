# Get 4 players

# Loop until a player reaches a score of 100..

#  Shuffle 52 cards

#  Deal to each of 4 players

#  Request 3 cards to discard from each player

#  Deal passed cards to each player

#  Loop until all cards played..

#   Locate player with 2C
#   Get card from that player
#   Get card from next 3 players
#   Determine which player won the trick
#   Add any points to that player
#   Mark winner as next player
#   repeat..

# Determine winner and 2nd, 3rd, 4th places
# Calculate statistics


# Cards are denoted as follows:
#  2-9, 10, Jack, Queen, King, Ace - 2-9, X, J, Q, K, A
#  Suits: Clubs, Diamonds, Spades, Hearts - C, D, S, H
#  eg XH = 10 of hearts
# Pass cards direction: left, right, across - L, R, A

# Interface between server and player

# Initialise game - other 3 players' details

# Deal - 13 cards

# Request 3 passed cards - direction

# Deal passed cards - 3 cards

# Request play card - list of current played cards, list of valid playable cards

# Report played round - 4 cards, points gained for each 4 players

# Game over - scores, order and placement of each 4 players

import random
from card import *
from player_random import RandomPlayer
from player_ai import AIPlayer

NUM_GAMES = 1  # 100

ROUND_LOGFILE = "rounds.log"


def shift(a, i):
    i %= len(a)
    return a[i:] + a[:i]


NUM_PLAYERS = 4
NUM_CARDS = len(DECK) // NUM_PLAYERS

wins = [0] * NUM_PLAYERS

for g in range(NUM_GAMES):

    players = [RandomPlayer(i) for i in range(3)] + [AIPlayer(3)]

    points_game = [0] * NUM_PLAYERS

    direction = 0

    play = True

    while play:

        #
        # Shuffle the deck
        #
        deck = DECK.copy()
        random.shuffle(deck)
        # print('deck:',serialize(deck))

        hands = [None] * NUM_PLAYERS

        #
        # Deal all the cards
        #
        cards_dealt = [None] * NUM_PLAYERS
        for i, player in enumerate(players):
            cards_dealt[i] = deck[i * NUM_CARDS : (i + 1) * NUM_CARDS]
            cards_dealt[i].sort()
            player.dealt(cards_dealt[i])
            hands[i] = cards_dealt[i].copy()

        # for i,player in enumerate(players):
        #    print(f'player: {player} cards: {serialize(hands[i])}')

        #
        # Get each player to pass 3 cards
        #
        cards_passed = [None] * NUM_PLAYERS
        cards_received = [None] * NUM_PLAYERS
        if direction != 3:
            for i, player in enumerate(players):
                cards = player.pass_cards(hands[i], direction)
                # print(f'player: {player} cards_passed: {cards} from: {hands[i]}')
                if len(cards) != 3:
                    print(f"player:{player} ERROR: passed {len(cards)} cards instead of 3")
                if not set(cards).issubset(set(hands[i])):
                    print(f"player:{player} ERROR: passed {serialize(cards)} which are not in {serialize(hands[i])}")
                cards_passed[i] = cards
                cards_passed[i].sort()
                for card in cards:
                    hands[i].remove(card)
                assert not set(cards_passed[i]).issubset(set(hands[i]))

            adj = -1 if direction == 0 else 1 if direction == 1 else 2
            for i, player in enumerate(players):
                j = (i + adj) % 4
                cards_received[i] = cards_passed[j]
                player.receive_cards(cards_received[i])
                hands[i].extend(cards_received[i])
                hands[i].sort()
                assert set(cards_received[i]).issubset(set(hands[i]))

        # for i,player in enumerate(players):
        #    print(f'player: {player} cards: {serialize(hands[i])}')

        #
        # Play the round
        #
        points_round = [0] * NUM_PLAYERS

        # Determine which player has the 2 of clubs
        for i in range(NUM_PLAYERS):
            if CARD_2C in hands[i]:
                lead = i
                break
        hearts_broken = False
        cards_played = [[] for _ in range(NUM_PLAYERS)]
        for turn in range(NUM_CARDS):
            # print('lead:', lead)
            lead_suit = None
            cards_in_turn = []
            for j in range(NUM_PLAYERS):
                p = (j + lead) % NUM_PLAYERS
                player = players[p]
                if turn == 0 and j == 0:
                    # 2 of clubs must be the first card played
                    playable = [CARD_2C]
                else:
                    playable = None
                    # See if player has any cards in the lead suit
                    if lead_suit is not None:
                        playable = list(filter(lambda x: in_suit(x, lead_suit), hands[p]))
                    if not playable:
                        # If not then include all player's cards
                        playable = hands[p]
                    if turn == 0:
                        # On first hand remove queen of spades
                        playable = list(filter(lambda x: (x != CARD_QS), playable))
                    if turn == 0 or (j == 0 and not hearts_broken):
                        # On first hand or if lead player and hearts not broken remove all hearts
                        playable = list(filter(lambda x: (not in_suit(x, HEARTS)), playable))
                    # If we end up with no playable cards then bring back the hearts
                    if not playable:
                        playable = list(filter(lambda x: in_suit(x, HEARTS), hands[p]))
                    if not playable:
                        print("ERROR: no playable cards from:", serialize(player.cards))
                card = player.play_turn(
                    turn, lead_suit, cards_in_turn, playable, shift(points_round, p + 1), shift(points_game, p + 1),
                )
                if card not in playable:
                    print(
                        "player:",
                        player,
                        "ERROR: palyed card %s which is not in the playable list of %s"
                        % (deserialize(card), deserialize(playable)),
                    )
                cards_in_turn.append(card)
                hands[p].remove(card)

                if j == 0:
                    _, lead_suit = decode(card)
                if not hearts_broken and in_suit(card, HEARTS):
                    # print('hearts broken')
                    hearts_broken = True
            # print('lead:',lead,'cards_in_turn:',serialize(cards_in_turn))

            # Keep track of each player's played cards
            for i, player in enumerate(players):
                p = (i - lead) % NUM_PLAYERS
                cards_played[i].append(cards_in_turn[p])
                # print('player:',player,'has played:',serialize(cards_played[i]))

            # Determine the winner of the hand
            max_c = None
            max_p = None
            for j, card in enumerate(cards_in_turn):
                c, s = decode(card)
                p = (j + lead) % NUM_PLAYERS
                if j == 0:
                    lead_suit = s
                    max_c = c
                    max_p = p
                elif s == lead_suit:
                    if c > max_c:
                        max_c = c
                        max_p = p

            # Calculate points for this hand
            points = len(list(filter(lambda x: in_suit(x, HEARTS), cards_in_turn)))
            if CARD_QS in cards_in_turn:
                points += 13

            if points == 26:
                # TODO Offer choice of +26 or -26
                for i in range(NUM_PLAYERS):
                    if i != max_p:
                        points_round[i] += 26
            else:
                points_round[max_p] += points

            for i, player in enumerate(players):
                p = (i - lead) % NUM_PLAYERS
                player.played_hand(cards_in_turn, cards_in_turn[p], points_round[i])

            lead = max_p

        #
        # Log the played cards along with their points
        #
        for i, player in enumerate(players):
            cards = set(cards_dealt[i])
            if cards_passed[i]:
                cards -= set(cards_passed[i])
            if cards_received[i]:
                cards |= set(cards_received[i])
            assert cards == set(cards_played[i])
            line = (
                cards_dealt[i]
                + (cards_passed[i] if direction != 3 else [CARDS_IN_DECK] * 3)
                + (cards_received[i] if direction != 3 else [CARDS_IN_DECK] * 3)
                + cards_played[i]
                + [points_round[i]]
            )
            with open(ROUND_LOGFILE, "ab") as f:
                f.write(bytes(line))

        direction = (direction + 1) % 4

        for i, points in enumerate(points_round):
            points_game[i] += points

        play = not list(filter(lambda x: x >= 100, points_game))

    print("end of game:", points_game)

    #
    # Inform each player of the final score
    #
    for i, player in enumerate(players):
        player.played_game(shift(points_game, i + 1))

    #
    # Determine which player has won
    #
    min_points = min(points_game)
    for i, points in enumerate(points_game):
        if points == min_points:
            wins[i] += 1

print("wins %:", [x * 100 // NUM_GAMES for x in wins])
