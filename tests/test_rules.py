import pytest

from card import *
from rules import Rules

# pytest_plugins = ["tests.fixtures.player"]

CARD_2 = 0
CARD_3 = 1
CARD_4 = 2
CARD_5 = 3
CARD_6 = 4
CARD_7 = 5
CARD_8 = 6
CARD_9 = 7
CARD_X = 8
CARD_J = 9
CARD_Q = 10
CARD_K = 11
CARD_A = 12


@pytest.mark.parametrize(
    "cards,score",
    [
        ((CARD_2, CARD_3, CARD_4, CARD_5), 0),
        ((CARD_Q, CARD_K, CARD_A), 100),
        ((CARD_4, CARD_6, CARD_8, CARD_X, CARD_Q), 24),
        ((CARD_2, CARD_8, CARD_A), 25),
    ],
)
def test_score(cards, score):
    ret = Rules._score(cards)
    assert ret == score


@pytest.mark.parametrize(
    "cards,avail,score",
    [
        ((CARD_2, CARD_3, CARD_4, CARD_5), (CARD_2, CARD_3, CARD_4, CARD_5, CARD_6), 0),
        ((CARD_Q, CARD_K, CARD_A), (CARD_Q, CARD_K, CARD_A), 0),
        (
            (CARD_4, CARD_6, CARD_8, CARD_X, CARD_Q),
            (CARD_3, CARD_4, CARD_5, CARD_6, CARD_7, CARD_8, CARD_9, CARD_X, CARD_J, CARD_Q),
            9,
        ),
        ((CARD_2, CARD_8, CARD_A), (CARD_2, CARD_4, CARD_6, CARD_8, CARD_X, CARD_Q, CARD_A), 8),
    ],
)
def test_score_with_avail(cards, avail, score):
    ret = Rules._score(cards, avail)
    assert ret == score


@pytest.mark.parametrize(
    "cards,result",
    [
        # Positive
        (["2C", "6C", "AS", "2H", "QC", "3D", "4D", "5D", "XH", "8D", "9D", "XD", "6S"], CARD_2C),
        # Negative
        (["4C", "7C", "8C", "XC", "4H", "5H", "KC", "9H", "6D", "QD", "3S", "5S", "7S"], None),
    ],
)
def test_pass_two_clubs(cards, result):
    cards = deserialize(cards)
    suits = split_into_suits(cards)
    ret = Rules._pass_two_clubs(suits)
    assert ret == result


@pytest.mark.parametrize(
    "cards,result",
    [
        # Positive
        (["2C", "4C", "QS", "KS", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2S", "3S"], CARD_QS),
        # Negative
        (["4C", "7C", "8C", "XC", "4H", "5H", "KC", "9H", "6D", "QD", "3S", "5S", "7S"], None),
    ],
)
def test_pass_queen_spades(cards, result):
    cards = deserialize(cards)
    suits = split_into_suits(cards)
    ret = Rules._pass_queen_spades(suits)
    assert ret == result


@pytest.mark.parametrize(
    "cards,result",
    [
        # Positive
        (["2C", "4C", "QS", "KD", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2S", "3S"], CARD_QS),
        # Negative
        (["4C", "7C", "8C", "XC", "4H", "5H", "KC", "9H", "6D", "QD", "3S", "5S", "7S"], None),
        # Negative when 4 or more spades
        (["8S", "QS", "6C", "AS", "8C", "4H", "KC", "7H", "3D", "5D", "7D", "AD", "2S"], None),
    ],
)
def test_pass_queen_spades_max_3_spades(cards, result):
    cards = deserialize(cards)
    suits = split_into_suits(cards)
    ret = Rules._pass_queen_spades_max_3_spades(suits)
    assert ret == result


@pytest.mark.parametrize(
    "cards,result",
    [
        # Positive Ace of Spades
        (["2C", "4C", "AS", "KD", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2D", "3H"], CARD_AS),
        # Positive King of Spades
        (["2C", "4C", "KS", "KD", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2D", "3H"], CARD_KS),
        # Positive Queen of Spades
        (["2C", "4C", "QS", "KD", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2D", "3H"], CARD_QS),
        # Negative
        (["2C", "4C", "JS", "QS", "XS", "AS", "KC", "3D", "6D", "AH", "2S", "6S", "7S"], None),
    ],
)
def test_pass_high_spades_no_lower(cards, result):
    cards = deserialize(cards)
    suits = split_into_suits(cards)
    ret = Rules._pass_high_spades_no_lower(suits)
    assert ret == result


@pytest.mark.parametrize(
    "cards,result",
    [
        # Positive a Club
        (["XS", "3H", "4H", "JC", "6H", "2D", "JH", "6D", "XD", "JD", "QD", "3S", "5S"], deserialize("JC")),
        # Positive a Diamond
        (["8S", "JS", "QS", "6C", "9C", "2H", "4H", "JD", "QH", "7C", "6D", "QD", "KH"], deserialize("QD")),
        # Positive a Heart
        (["2C", "6C", "AS", "3H", "AC", "3D", "XH", "JH", "7D", "KH", "AH", "KD", "3S"], deserialize("AH")),
        # Negative
        (["2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "XS", "JS", "QS", "KS", "AS"], None),
    ],
)
def test_pass_high_except_spades(cards, result):
    cards = deserialize(cards)
    suits = split_into_suits(cards)
    ret = Rules._pass_high_except_spades(suits)
    assert ret == result


@pytest.mark.parametrize(
    "cards,result",
    [
        # Positive a Club from 2 Clubs, 6 Diamonds, 3 Hearts
        (["7C", "2H", "AC", "3D", "JH", "6D", "AH", "9D", "JD", "QD", "AD", "6S", "7S"], deserialize("AC")),
        # Positive a Diamond from 4 Clubs, 2 Diamonds, 4 Hearts
        (["3C", "KS", "7C", "XC", "6H", "AC", "2D", "9H", "5D", "QH", "6D", "AH", "3S"], deserialize("6D")),
        # Positive a Heart from 7 Clubs, 3 Diamonds, 2 Hearts
        (["2C", "3C", "4C", "7C", "8C", "QC", "AC", "XH", "JH", "6D", "QD", "AD", "5S"], deserialize("JH")),
        # Positive a Diamond from 6 Clubs, 3 Diamonds, 3 Hearts
        (["2C", "3H", "4C", "7C", "8C", "QC", "AC", "XH", "JH", "6D", "QD", "AD", "5S"], deserialize("AD")),
        # Positive a Heart from 6 Clubs, 3 Diamonds, 3 Hearts
        (["2C", "3D", "4C", "7C", "8C", "QC", "AC", "XD", "JD", "6H", "QH", "AH", "5S"], deserialize("AH")),
        # Negative from 13 Spades
        (["2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "XS", "JS", "QS", "KS", "AS"], None),
    ],
)
def test_pass_smallest_suit_except_spades(cards, result):
    cards = deserialize(cards)
    suits = split_into_suits(cards)
    ret = Rules._pass_smallest_suit_except_spades(suits)
    assert ret == result


@pytest.mark.parametrize(
    "cards,result",
    [
        # Positive a Club from 2 Clubs, 6 Diamonds, 3 Hearts
        (["7C", "2H", "AC", "3D", "JH", "6D", "AH", "9D", "JD", "QD", "AD", "6S", "7S"], deserialize("AC")),
        # Positive a Heart from 2 Clubs, 6 Diamonds, 3 Hearts
        (["3C", "2H", "6C", "3D", "JH", "6D", "AH", "9D", "JD", "QD", "AD", "6S", "7S"], deserialize("AH")),
        # Positive a Diamond from 4 Clubs, 2 Diamonds, 4 Hearts
        (["3C", "KS", "7C", "XC", "6H", "AC", "2D", "9H", "5D", "QH", "6D", "AH", "3S"], deserialize("6D")),
        # Positive a Diamond from 6 Clubs, 3 Diamonds, 3 Hearts
        (["2C", "3H", "4C", "7C", "8C", "QC", "AC", "XH", "JH", "6D", "QD", "AD", "5S"], deserialize("AD")),
        # Positive a Heart from 6 Clubs, 3 Diamonds, 3 Hearts
        (["2C", "3D", "4C", "7C", "8C", "QC", "AC", "XD", "JD", "6H", "QH", "AH", "5S"], deserialize("AH")),
        # Negative from 4 Clubs, 4 Diamonds, 1 Spade, 4 Hearts
        (["2C", "3C", "4C", "5C", "6D", "7D", "8D", "9D", "XS", "JH", "QH", "KH", "AH"], None),
        # Negative from 13 Spades
        (["2S", "3S", "4S", "5S", "6S", "7S", "8S", "9S", "XS", "JS", "QS", "KS", "AS"], None),
    ],
)
def test_pass_suits_max_3_except_spades(cards, result):
    cards = deserialize(cards)
    suits = split_into_suits(cards)
    ret = Rules._pass_suits_max_3_except_spades(suits)
    assert ret == result
