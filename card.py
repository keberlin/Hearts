CARDS_IN_SUIT = 13
SUITS_IN_DECK = 4
CARDS_IN_DECK = CARDS_IN_SUIT * SUITS_IN_DECK

CLUBS = 0
DIAMONDS = 1
SPADES = 2
HEARTS = 3


def decode(i):
    return i % CARDS_IN_SUIT, i // CARDS_IN_SUIT


def in_suit(i, s):
    return s * CARDS_IN_SUIT <= i < (s + 1) * CARDS_IN_SUIT


DECK = [i for i in range(CARDS_IN_DECK)]

NM_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "X", "J", "Q", "K", "A"]
NM_SUITS = ["C", "D", "S", "H"]


def serialize(v, sort=False):
    if type(v) is list:
        return list(map(lambda x: serialize(x), sorted(v) if sort else v))
    if type(v) is set:
        return serialize(list(v))
    if v is None:
        return ""
    if v >= CARDS_IN_DECK:
        return "--"
    c, s = decode(v)
    return NM_VALUES[c] + NM_SUITS[s]


def serializedb(v, sort=False):
    return "".join(serialize(v, sort))


def deserialize(nm):
    if type(nm) is list:
        return list(map(lambda x: deserialize(x), nm))
    if type(nm) is set:
        return deserialize(list(nm))
    return NM_SUITS.index(nm[1]) * CARDS_IN_SUIT + NM_VALUES.index(nm[0])


CARD_2C = deserialize("2C")
CARD_QS = deserialize("QS")
CARD_KS = deserialize("KS")
CARD_AS = deserialize("AS")


def split_into_suits(cards):
    return [sorted(list(filter(lambda x: in_suit(x, s), cards))) for s in range(SUITS_IN_DECK)]


def calc_points(cards):
    # Calculate points for this hand
    points = len(list(filter(lambda x: in_suit(x, HEARTS), cards)))
    if CARD_QS in cards:
        points += 13
    return points
