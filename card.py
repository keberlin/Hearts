CARDS_IN_SUIT = 13
SUITS_IN_DECK = 4
CARDS_IN_DECK = CARDS_IN_SUIT*SUITS_IN_DECK

CLUBS = 0
DIAMONDS = 1
SPADES = 2
HEARTS = 3

def decode(i): return i%CARDS_IN_SUIT,i//CARDS_IN_SUIT

def in_suit(i,s): return s*CARDS_IN_SUIT <= i < (s+1)*CARDS_IN_SUIT

DECK = [i for i in range(CARDS_IN_DECK)]

NM_VALUES = ['2','3','4','5','6','7','8','9','X','J','Q','K','A']
NM_SUITS = ['C','D','S','H']

def serialize(i):
    if type(i) is list:
        return list(map(lambda x:serialize(x),i))
    c,s = decode(i)
    return NM_VALUES[c]+NM_SUITS[s]

def deserialize(nm):
    return NM_SUITS.index(nm[1])*CARDS_IN_SUIT+NM_VALUES.index(nm[0])

CARD_2C = deserialize('2C')
CARD_QS = deserialize('QS')
CARD_KS = deserialize('KS')
CARD_AS = deserialize('AS')
