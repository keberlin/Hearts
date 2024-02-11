import argparse
import copy
from datetime import datetime
import json
import logging
import os
import random

from card import *
from database import db_init, HEARTS_DB_URI
from model import GameModel, HandModel, PassingModel, PlayerModel
from player_ai import AIPlayer
from player_heuristic import HeuristicPlayer
from player_random import RandomPlayer
from utils import ranking

logger = logging.getLogger()
logging.basicConfig(filename="/var/log/hearts/log", level=logging.DEBUG)

session = db_init(HEARTS_DB_URI)


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


parser = argparse.ArgumentParser(description="Hearts card game harness.")
parser.add_argument("-g", dest="games", type=int, default=1, help="Number of games to play", required=False)
args = parser.parse_args()

games = args.games


def shift(a, i):
    i %= len(a)
    return a[i:] + a[:i]


NUM_PLAYERS = 4
NUM_CARDS = len(DECK) // NUM_PLAYERS


def play_hand(cards_dealt, direction, cards_passed, cards_received, cards_playing, points_game):
    #
    # Play the hand
    #
    hands = copy.deepcopy(cards_playing)

    points_hand = [0] * NUM_PLAYERS

    # Determine which player has the 2 of clubs
    for i in range(NUM_PLAYERS):
        if CARD_2C in hands[i]:
            lead = i
            break

    # Keep track of hearts being broken
    hearts_broken = False

    cards_played = [[] for _ in range(NUM_PLAYERS)]
    turns_played = []
    cards_remaining = list(DECK)

    # Play each of the turns
    for turn in range(NUM_CARDS):
        logger.debug(f"lead: {lead} {players[lead]}")
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
                    logger.error(f"ERROR: no playable cards from {serialize(hands[p],sort=True)}")
                    exit(1)
            # Player: play_turn
            card = player.play_turn(
                turn,
                lead_suit,
                cards_in_turn,
                list(hands[p]),  # deliberately copy the list
                playable,
                shift(points_hand, p),
                shift(points_game, p),
                [((x - p) % NUM_PLAYERS, y) for x, y, _ in turns_played],
                cards_remaining,
                cards_dealt[p],
                direction,
                cards_passed[p],
                cards_received[p],
                cards_playing[p],
            )
            if card not in playable:
                logger.error(
                    f"ERROR: player: {player} played card {serialize(card)} which is not in the playable list of {serialize(playable,sort=True)}"
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
                logger.debug("hearts broken")
                hearts_broken = True
        logger.debug(f"lead: {lead} {players[lead]}, cards played in turn {turn}: {serialize(cards_in_turn)}")

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

        # Calculate points for each player
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
            points_hand[i] += points_in_turn[i]

        for i, player in enumerate(players):
            p = (i - lead) % NUM_PLAYERS
            # Player: played_hand
            player.played_hand(cards_in_turn, cards_in_turn[p], points_hand[i])

        # Keep track of each round's who led and played cards
        turns_played.append((lead, cards_in_turn, points_in_turn))

        lead = max_p

    return turns_played, points_hand


def play_game(game_id, players, player_ids):
    points_game = [0] * NUM_PLAYERS

    rounds_played = [[] for _ in range(NUM_PLAYERS)]

    direction = 0

    play = True

    while play:
        #
        # Shuffle the deck
        #
        deck = list(DECK)
        random.shuffle(deck)

        #
        # Deal all the cards
        #
        cards_dealt = [None] * NUM_PLAYERS
        for i, player in enumerate(players):
            cards_dealt[i] = deck[i * NUM_CARDS : (i + 1) * NUM_CARDS]
            assert len(cards_dealt[i]) == NUM_CARDS
            # Player: dealt
            player.dealt(list(cards_dealt[i]))  # deliberately copy the list

        for i, player in enumerate(players):
            logger.debug(f"cards dealt for player {i} {player}: {serialize(cards_dealt[i],sort=True)}")

        #
        # Get each player to pass 3 cards
        #
        cards_passed = [None] * NUM_PLAYERS
        cards_received = [None] * NUM_PLAYERS
        if direction != 3:
            for i, player in enumerate(players):
                # Player: pass_cards
                cards = player.pass_cards(list(cards_dealt[i]), direction)  # deliberately copy the list
                logger.debug(f"cards passed from player {i} {player}: {cards}")
                if len(cards) != 3:
                    logger.error(f"ERROR: player {player} passed {len(cards)} cards instead of 3")
                    exit(1)
                if not set(cards).issubset(set(cards_dealt[i])):
                    logger.error(
                        f"ERROR: player {player} passed {serialize(cards,sort=True)} which are not in {serialize(cards_dealt[i],sort=True)}"
                    )
                    exit(1)
                cards_passed[i] = cards

            adj = -1 if direction == 0 else 1 if direction == 1 else 2
            for i, player in enumerate(players):
                j = (i + adj) % NUM_PLAYERS
                cards_received[i] = cards_passed[j]
                # Player: receive_cards
                player.receive_cards(cards_received[i].copy())

        cards_playing = [None] * NUM_PLAYERS
        for i, player in enumerate(players):
            cards_playing[i] = list(cards_dealt[i])  # deliberately copy the list
            assert len(cards_playing[i]) == NUM_CARDS
            if direction != 3:
                cards_playing[i] = list(set(cards_playing[i]) - set(cards_passed[i]))
                assert not set(cards_passed[i]).issubset(set(cards_playing[i]))
                cards_playing[i] = list(set(cards_playing[i]) | set(cards_received[i]))
                assert set(cards_received[i]).issubset(set(cards_playing[i]))
                assert len(cards_playing[i]) == NUM_CARDS

        for i, player in enumerate(players):
            logger.debug(f"cards after passing for player {i} {player}: {serialize(cards_playing[i],sort=True)}")

        turns_played, points_hand = play_hand(
            cards_dealt, direction, cards_passed, cards_received, cards_playing, points_game
        )

        #
        # Update the passing db table
        #
        if direction != 3:
            for i in range(NUM_PLAYERS):
                entry = PassingModel(
                    dealt=serializedb(cards_dealt[i], sort=True),
                    direction=direction,
                    passed=serializedb(cards_passed[i], sort=True),
                    points=-26 if points_hand[i] == 26 else points_hand[i],
                )
                session.add(entry)
            session.commit()

        #
        # Update the hands db table
        #
        for i, player in enumerate(players):
            entry = HandModel(
                game=game_id,
                player=player_ids[i],
                dealt=serializedb(cards_dealt[i], sort=True),
                direction=direction,
                passed=serializedb(cards_passed[i], sort=True),
                received=serializedb(cards_received[i], sort=True),
                playing=serializedb(cards_playing[i], sort=True),
                turns=" ".join([f"{(x-i)%NUM_PLAYERS} {serializedb(y)}" for x, y, _ in turns_played]),
                points=points_hand[i],
            )
            session.add(entry)
        session.commit()

        #
        # Keep track of played games
        #
        for i, player in enumerate(players):
            rounds_played[i].append(
                (
                    [((x - i) % NUM_PLAYERS, y, shift(z, i)) for x, y, z in turns_played],
                    cards_dealt[i],
                    direction,
                    cards_passed[i],
                    cards_received[i],
                )
            )

        direction = (direction + 1) % 4

        for i, points in enumerate(points_hand):
            points_game[i] += points

        play = not list(filter(lambda x: x >= 100, points_game))

    logger.info(f"end of game: {points_game}")

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

    return points_game


num_games = 0

while True:
    players = [AIPlayer(0), AIPlayer(1), AIPlayer(2), HeuristicPlayer(3)]

    player_ids = []
    for player in players:
        username = str(player)
        entry = session.query(PlayerModel).filter(PlayerModel.name == username).one_or_none()
        if not entry:
            entry = PlayerModel(name=username)
            session.add(entry)
            session.flush()
            assert entry.id
        player_ids.append(entry.id)

    game = GameModel(
        start=datetime.utcnow(),
        player_1=player_ids[0],
        player_2=player_ids[1],
        player_3=player_ids[2],
        player_4=player_ids[3],
    )
    session.add(game)
    session.flush()
    assert game.id

    points = play_game(game.id, players, player_ids)

    game.points_1 = points[0]
    game.points_2 = points[1]
    game.points_3 = points[2]
    game.points_4 = points[3]
    game.position_1 = ranking(points[0], points)
    game.position_2 = ranking(points[1], points)
    game.position_3 = ranking(points[2], points)
    game.position_4 = ranking(points[3], points)
    game.finish = datetime.utcnow()
    session.commit()

    num_games += 1

    if num_games >= games:
        break
