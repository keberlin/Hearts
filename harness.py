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
CLUBS = 0
DIAMONDS = 1
SPADES = 2
HEARTS = 3

DECK = [i for i in range(SUITS_IN_DECK*CARDS_IN_SUIT)]

NM_VALUES = ['2','3','4','5','6','7','8','9','X','J','Q','K','A']
NM_SUITS = ['C','D','S','H']

def decode(i): return i%CARDS_IN_SUIT,i//CARDS_IN_SUIT

def serialize(i):
    if type(i) is list:
        return list(map(lambda x:serialize(x),i))
    c,s = decode(i)
    return NM_VALUES[c]+NM_SUITS[s]

def deserialize(nm):
    return NM_SUITS.index(nm[1])*SUITS_IN_DECK+NM_VALUES.index(nm[0])

CARD_2C = deserialize('2C')
CARD_QS = deserialize('QS')

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
        print(self.id,'play_turn:',serialize(playable))
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

distribution = [None for i in range(len(DECK))]

def player_cards(p,suit=None):
    cards = list(filter(lambda x: x is not None, [i if l == p else None for i, l in enumerate(distribution)]))
    if suit is not None:
        cards = list(filter(lambda x:suit*CARDS_IN_SUIT <= x < (suit+1)*CARDS_IN_SUIT,cards))
    return cards

for i,player in enumerate(players):
    cards = deck[i*NUM_CARDS:(i+1)*NUM_CARDS]
    player.deal(cards)
    for card in cards:
        distribution[card] = i

if direction != 3:
    passed_cards = []
    for i, player in enumerate(players):
        cards = player.pass_cards(direction)
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

print('distribution:',distribution)
for i in range(NUM_PLAYERS):
    for s in range(SUITS_IN_DECK):
        cards = player_cards(i,s)
        print(i,s,len(cards),serialize(cards))

# Determine which player has the 2 of clubs
lead = distribution[CARD_2C]
for i in range(NUM_CARDS):
    print('lead:', lead)
    lead_s = None
    played_cards = []
    for j in range(NUM_PLAYERS):
        p = (j+lead)%4
        player = players[p]
        if i==0 and j==0:
            playable = [CARD_2C]
        else:
            playable = player_cards(p,lead_s)
            if not playable:
                playable = player_cards(p)
            if i==0:
                # On first hand remove queen of spades and all hearts
                playable = list(filter(lambda x:(x!=CARD_QS and not HEARTS*CARDS_IN_SUIT <= x < (HEARTS+1)*CARDS_IN_SUIT),playable))
        card = player.play_turn(played_cards,playable)
        if j==0:
            _,lead_s = decode(card)
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
            lead_s = s
            max_c = c
            max_p = p
        if s==lead_s:
            if c>max_c:
                max_c = c
                max_p = p
    lead = max_p
