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

import argparse
import json
import os
import random

from card import *
from player_ai import AIPlayer
from player_random import RandomPlayer

parser = argparse.ArgumentParser(description="Hearts card game harness.")
parser.add_argument(
    "-f", dest="force_lose", action="store_true", default=False, help="Play until AI player loses", required=False
)
parser.add_argument("-g", dest="games", type=int, nargs=1, default=1, help="Number of games to play", required=False)
args = parser.parse_args()

games = args.games[0]

ROUND_LOGFILE = "rounds.log"


def shift(a, i):
    i %= len(a)
    return a[i:] + a[:i]


NUM_PLAYERS = 4
NUM_CARDS = len(DECK) // NUM_PLAYERS

STATS_JSON_FILE = "stats.json"
STATS_RESULTS_FILE = "stats.txt"

historic_statistics = {"players": {},'games_played':0}

if os.path.isfile(STATS_JSON_FILE):
    with open(STATS_JSON_FILE, "r") as f:
        historic_statistics = json.loads(f.read())

num_games = 0

while True:

    if not (args.force_lose or num_games < games):
        break

    players = [AIPlayer(i) for i in range(4)]

    for player in players:
        username = str(player)
        if not username in historic_statistics["players"]:
            historic_statistics["players"][username] = [0, 0]
        historic_statistics["players"][username][0] += 1

    points_game = [0] * NUM_PLAYERS

    rounds_played = [[] for _ in range(NUM_PLAYERS)]

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
            cards_dealt[i] = set(deck[i * NUM_CARDS : (i + 1) * NUM_CARDS])
            # Player: dealt
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
                # Player: pass_cards
                cards = set(player.pass_cards(set(hands[i]), direction))
                # print(f'player: {player} cards_passed: {cards} from: {hands[i]}')
                if len(cards) != 3:
                    print(f"ERROR: player {player} passed {len(cards)} cards instead of 3")
                    exit(1)
                if not cards.issubset(hands[i]):
                    print(f"ERROR: player {player} passed {serialize(cards)} which are not in {serialize(hands[i])}")
                    exit(1)
                cards_passed[i] = cards
                hands[i] -= cards_passed[i]
                assert not cards_passed[i].issubset(hands[i])

            adj = -1 if direction == 0 else 1 if direction == 1 else 2
            for i, player in enumerate(players):
                j = (i + adj) % NUM_PLAYERS
                cards_received[i] = cards_passed[j]
                player.receive_cards(cards_received[i])
                hands[i] |= cards_received[i]
                assert cards_received[i].issubset(hands[i])

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
        turns_played = []
        cards_remaining = set(DECK)
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
                        playable = list(hands[p])
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
                        print(f"ERROR: no playable cards from {serialize(hands[p])}")
                        exit(1)
                # Player: play_turn
                card = player.play_turn(
                    turn,
                    lead_suit,
                    cards_in_turn,
                    set(hands[p]),
                    playable,
                    shift(points_round, p),
                    shift(points_game, p),
                    [((x - p) % NUM_PLAYERS, y) for x, y, _ in turns_played],
                    cards_remaining,
                    cards_dealt[p],
                    cards_passed[p],
                    cards_received[p],
                    direction,
                )
                if card not in playable:
                    print(
                        f"ERROR: player: {player} played card {serialize(card)} which is not in the playable list of {serialize(playable)}"
                    )
                    exit(1)

                # Keep track of the cards played in this hand so far
                cards_in_turn.append(card)
                # Remove this card from the player's current hand
                hands[p].remove(card)
                # Keep track of each player's played cards
                cards_played[p].append(card)
                # Keep track of the remaining cards to be played
                cards_remaining.remove(card)

                if j == 0:
                    _, lead_suit = decode(card)
                if not hearts_broken and in_suit(card, HEARTS):
                    # print('hearts broken')
                    hearts_broken = True
            # print('lead:',lead,'cards_in_turn:',serialize(cards_in_turn))

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
            points = calc_points(cards_in_turn)

            # Calcluate points for each player
            points_in_turn = [0] * NUM_PLAYERS

            if points == 26:
                # TODO Offer choice of +26 or -26
                for i in range(NUM_PLAYERS):
                    if i != max_p:
                        points_in_turn[i] = 26
            else:
                points_in_turn[max_p] = points

            # Calculate the accumulated points for each player
            for i in range(NUM_PLAYERS):
                points_round[i] += points_in_turn[i]

            for i, player in enumerate(players):
                p = (i - lead) % NUM_PLAYERS
                # Player: played_hand
                player.played_hand(cards_in_turn, cards_in_turn[p], points_round[i])

            # Keep track of each round's who led and played cards
            turns_played.append((lead, cards_in_turn, points_in_turn))

            lead = max_p

        # Keep track of all hands played for the whole game
        for i, player in enumerate(players):
            rounds_played[i].append(
                (
                    [((x - i) % NUM_PLAYERS, y, shift(z, i)) for x, y, z in turns_played],
                    cards_dealt[i],
                    cards_passed[i],
                    cards_received[i],
                    direction,
                )
            )

        #
        # Log the played cards along with their points
        #
        for i, player in enumerate(players):
            cards = cards_dealt[i].copy()
            if cards_passed[i]:
                cards -= cards_passed[i]
            if cards_received[i]:
                cards |= cards_received[i]
            assert cards == set(cards_played[i])
            line = (
                sorted(list(cards_dealt[i]))
                + (sorted(list(cards_passed[i])) if cards_passed[i] else [CARDS_IN_DECK] * 3)
                + (sorted(list(cards_received[i])) if cards_received[i] else [CARDS_IN_DECK] * 3)
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
        # Player: played_game
        player.played_game(shift(points_game, i), rounds_played[i])

    #
    # Determine which player has won
    #
    min_points = min(points_game)
    winners = []
    for i in range(NUM_PLAYERS):
        if points_game[i] == min_points:
            winners.append(i)
    max_points = max(points_game)
    losers = []
    for i in range(NUM_PLAYERS):
        if points_game[i] == max_points:
            losers.append(i)

    # Keep track of how many historic_statistics each player has
    for i in winners:
        username = str(players[i])
        historic_statistics["players"][username][1] += 1

    if args.force_lose and 3 in losers:
        break

    num_games += 1

historic_statistics["games_played"] += num_games
historic_statistics["number_of_players"] = len(historic_statistics["players"])

with open(STATS_JSON_FILE, "w") as f:
    f.write(json.dumps(historic_statistics, indent=4))

with open(STATS_RESULTS_FILE, "w") as f:
    # Only include usernames who have played 200 or more games
    stats = [
        (k, v[0], v[1], v[1] * 100 / v[0])
        for k, v in filter(lambda x: x[1][0] >= 200, historic_statistics["players"].items())
    ]
    stats.sort(key=lambda x: x[3], reverse=False)
    for v in stats:
        f.write(f"username: {v[0]}, played: {v[1]}, won: {v[2]} ({v[3]:.2f}%)\n")
