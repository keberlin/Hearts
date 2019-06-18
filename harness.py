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
from distribution import *
from player import *

NUM_GAMES = 20

def shift(a,i):
    i %= len(a)
    return a[i:]+a[:i]

NUM_PLAYERS = 4
NUM_CARDS = len(DECK)//NUM_PLAYERS

players = [RandomPlayer(i) for i in range(3)] + [AIPlayer(3)]
wins = [0 for i in range(len(players))]

for g in range(NUM_GAMES):

    player_points = [0 for i in range(NUM_PLAYERS)]

    direction = 0

    round = 1

    play = True

    while (play):

        print('round:',round)

        deck = DECK.copy()
        random.shuffle(deck)
        #print('deck:',serialize(deck))

        distribution = Distribution()

        for i,player in enumerate(players):
            cards = deck[i*NUM_CARDS:(i+1)*NUM_CARDS]
            player.deal(cards)
            for card in cards:
                distribution[card] = i
        for i,player in enumerate(players):
            print('player',i,'cards:',serialize(player.cards))

        if direction != 3:
            passed_cards = []
            for i, player in enumerate(players):
                cards = player.pass_cards(direction)
                if len(cards)!=3:
                    print('player:',player,'ERROR: passed %s cards instead of 3'%len(cards))
                passed_cards.append(cards)
                for card in cards:
                    distribution[card] = None

            adj = -1 if direction == 0 else 1 if direction == 1 else 2
            for i, player in enumerate(players):
                j = (i + adj) % 4
                cards = passed_cards[j]
                player.deal(cards)
                for card in cards:
                    distribution[card] = i

        for i in range(NUM_PLAYERS):
            for s in range(SUITS_IN_DECK):
                cards = distribution.player_cards(i,s)
                #print(i,s,len(cards),serialize(cards))

        hand_points = [0 for i in range(NUM_PLAYERS)]

        # Determine which player has the 2 of clubs
        lead = distribution[CARD_2C]
        hearts_broken = False
        for i in range(NUM_CARDS):
            print('lead:', lead)
            lead_suit = None
            played_cards = []
            for j in range(NUM_PLAYERS):
                p = (j+lead)%4
                player = players[p]
                if i==0 and j==0:
                    # 2 of clubs must be the first card played
                    playable = [CARD_2C]
                else:
                    # See if player has any cards in the lead suit
                    playable = distribution.player_cards(p,lead_suit)
                    if not playable:
                        # If not then include all player's cards
                        playable = distribution.player_cards(p)
                    if i==0:
                        # On first hand remove queen of spades and all hearts
                        playable = list(filter(lambda x:(x!=CARD_QS),playable))
                    if i==0 or (j==0 and not hearts_broken):
                        # On first hand or if lead player and hearts not broken remove all hearts
                        playable = list(filter(lambda x: (not in_suit(x, HEARTS)), playable))
                    # If we end up with no playable cards then bring back the hearts
                    if not playable:
                        playable = distribution.player_cards(p, HEARTS)
                    if not playable:
                        print('ERROR: no playable cards from:',serialize(player.cards))
                card = player.play_turn(round,lead_suit,played_cards,playable)
                if card not in playable:
                    print('player:',player,'ERROR: palyed card %s which is not in the playable list of %s'%(deserialize(card),deserialize(playable)))
                if j==0:
                    _,lead_suit = decode(card)
                if not hearts_broken and in_suit(card,HEARTS):
                    print('hearts broken')
                    hearts_broken = True
                distribution[card] = None
                played_cards.append(card)
            print('played_cards:',serialize(played_cards))

            # Determine the winner of the hand
            max_c = None
            max_p = None
            for j, played_card in enumerate(played_cards):
                c,s = decode(played_card)
                p = (j+lead)%4
                if j==0:
                    lead_suit = s
                    max_c = c
                    max_p = p
                if s==lead_suit:
                    if c>max_c:
                        max_c = c
                        max_p = p

            # Calculate points for this hand
            points = len(list(filter(lambda x:in_suit(x,HEARTS),played_cards)))
            if CARD_QS in played_cards: points += 13
            if points: hand_points[max_p] += points
            lead = max_p

            for j,player in enumerate(players):
                player.played_hand(shift(played_cards,j+1+lead),shift(hand_points,j+1+lead))

        for i, points in enumerate(hand_points):
            player_points[i] += points

        direction = (direction+1)%4

        round += 1

        play = not list(filter(lambda x:x>=100,player_points))

    print('end of game:',player_points)

    min_points = min(player_points)
    for p,points in enumerate(player_points):
        if points==min_points: wins[p] += 1

print('wins:',[str(x*100//NUM_GAMES)+'%' for x in wins])
