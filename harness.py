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

import itertools, random

CARDS_IN_SUIT = 13
SUITS_IN_DECK = 4

DECK = [i for i in range(SUITS_IN_DECK*CARDS_IN_SUIT)]

NM_VALUES = ['2','3','4','5','6','7','8','9','X','J','Q','K','A']
NM_SUITS = ['C','D','S','H']

def serialize(i):
    if type(i) is list:
        return list(map(lambda x:serialize(x),i))
    c,s = i%CARDS_IN_SUIT,i//CARDS_IN_SUIT
    return NM_VALUES[c]+NM_SUITS[s]

def deserialize(nm):
    return NM_SUITS.index(nm[1])*SUITS_IN_DECK+NM_VALUES.index(nm[0])

class Player():
    def __init__(self,id):
        self.id = id
        self.cards = []

    def deal(self,cards):
        print(self.id,'deal:',serialize(cards))
        self.cards += cards
        print(self.id,'cards:',serialize(self.cards))

    def pass_cards(self,direction):
        # TODO Determine best cards to pass
        ret = []
        for i in range(3):
            r = random.choice(self.cards)
            self.cards.remove(r)
            ret.append(r)
        print(self.id,'pass_cards:',serialize(ret))
        print(self.id,'cards:',serialize(self.cards))
        return ret

    def play_turn(self,round,playable):
        # TODO Determine best card to play
        ret = random.choice(playable)
        self.cards.remove(ret)
        return ret

NUM_PLAYERS = 4
NUM_CARDS = len(DECK)//NUM_PLAYERS

players = [Player(i) for i in range(NUM_PLAYERS)]

direction = 0

deck = DECK.copy()
random.shuffle(deck)
print('deck:',serialize(deck))

locations = [None for i in range(len(DECK))]

def player_cards(p):
    return list(filter(lambda x:x is not None,[i if l==p else None for i,l in enumerate(locations)]))

for i,player in enumerate(players):
    cards = deck[i*NUM_CARDS:(i+1)*NUM_CARDS]
    player.deal(cards)
    for card in cards:
        locations[card] = i

if direction != 3:
    passed_cards = []
    for i, player in enumerate(players):
        cards = player.pass_cards(direction)
        passed_cards.append(cards)
        for card in cards:
            locations[card] = None

    adj = -1 if direction == 0 else 1 if direction == 1 else 2
    for i, player in enumerate(players):
        j = (i + adj) % 4
        cards = passed_cards[j]
        player.deal(cards)
        for card in cards:
            locations[card] = i

print('locations:',locations)
for i in range(NUM_PLAYERS):
    cards = player_cards(i)
    print(i,len(cards),serialize(cards))

# Determine which player has the 2 of clubs
lead = locations[deserialize('2C')]
for i in range(NUM_CARDS):
    print('lead:', lead)
    played_cards = []
    for j in range(NUM_PLAYERS):
        p = (lead+j)%4
        player = players[p]
        playable = player_cards(p)
        card = player.play_turn(played_cards,playable)
        locations[card] = None
        played_cards.append(card)