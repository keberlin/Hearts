import re

CARDS_IN_SUIT = 13
SUITS_IN_DECK = 4
CARDS_IN_DECK = CARDS_IN_SUIT * SUITS_IN_DECK

CLUBS = 0
DIAMONDS = 1
SPADES = 2
HEARTS = 3

CHAR_CLUBS = "\u2667"
CHAR_DIAMONDS = "\u2662"
CHAR_SPADES = "\u2664"
CHAR_HEARTS = "\u2661"


def encode(s, v):
    return s * CARDS_IN_SUIT + v


def decode(i):
    return i % CARDS_IN_SUIT, i // CARDS_IN_SUIT


def in_suit(i, s):
    return s * CARDS_IN_SUIT <= i < (s + 1) * CARDS_IN_SUIT


DECK = [i for i in range(CARDS_IN_DECK)]

NM_SUITS = ["C", "D", "S", "H"]
NM_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "X", "J", "Q", "K", "A"]


def card(s, v):
    return encode(NM_SUITS.index(s), NM_VALUES.index(v))


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


TEXT_BLACK = "\033[30;47m"
TEXT_RESET = "\033[37;40m"
TEXT_RED = "\033[31;40m"


def serializepr(v, sort=False):
    return " ".join(serialize(v, sort))


def serializeco(v, sort=False):
    print(f"{serialize(v,sort)}")
    s = " ".join(serialize(v, sort))
    s = re.sub(r"([23456789XJQK])", r"\033[30;47m\1\033[37;40m", s)
    s = re.sub(r"([CS])", r"\033[30;47m\1\033[37;40m", s)
    s = re.sub(r"([DH])", r"\033[31;47m\1\033[37;40m", s)
    return s


def serializedb(v, sort=False):
    return "".join(serialize(v, sort))


def deserialize(nm):
    if type(nm) is list:
        return list(map(lambda x: deserialize(x), nm))
    if type(nm) is set:
        return deserialize(list(nm))
    return card(nm[1], nm[0])


def deserializedb(v):
    return [deserialize(v[i : i + 2]) for i in range(0, len(v), 2)]


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
