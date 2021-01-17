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
            10,
        ),
        ((CARD_2, CARD_8, CARD_A), (CARD_2, CARD_4, CARD_6, CARD_8, CARD_X, CARD_Q, CARD_A), 8),
    ],
)
def test_score_with_avail(cards, avail, score):
    ret = Rules._score(cards, avail)
    assert ret == score


def test_pass_two_clubs():
    # Test the 2 of Clubs gets returned
    cards = deserialize(["2C", "6C", "AS", "2H", "QC", "3D", "4D", "5D", "XH", "8D", "9D", "XD", "6S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_two_clubs(suits)
    assert ret == CARD_2C

    # Test the 2 of Clubs doesn't get returned
    cards = deserialize(["4C", "7C", "8C", "XC", "4H", "5H", "KC", "9H", "6D", "QD", "3S", "5S", "7S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_two_clubs(suits)
    assert not ret


def test_pass_queen_spades():
    # Test the Queen of Spades gets returned
    cards = deserialize(["2C", "4C", "QS", "KS", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2S", "3S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_queen_spades(suits)
    assert ret == CARD_QS

    # Test the Queen of Spades doesn't get returned
    cards = deserialize(["4C", "7C", "8C", "XC", "4H", "5H", "KC", "9H", "6D", "QD", "3S", "5S", "7S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_queen_spades(suits)
    assert not ret


def test_pass_queen_spades_if_less_than_4_spades():
    # Test the Queen of Spades gets returned
    cards = deserialize(["2C", "4C", "QS", "KD", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2S", "3S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_queen_spades_if_less_than_4_spades(suits)
    assert ret == CARD_QS

    # Test the Queen of Spades doesn't get returned
    cards = deserialize(["4C", "7C", "8C", "XC", "4H", "5H", "KC", "9H", "6D", "QD", "3S", "5S", "7S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_queen_spades_if_less_than_4_spades(suits)
    assert not ret

    # Test the Queen of Spades doesn't get returned when too many Spades
    cards = deserialize(["8S", "QS", "6C", "AS", "8C", "4H", "KC", "7H", "3D", "5D", "7D", "AD", "2S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_queen_spades_if_less_than_4_spades(suits)
    assert not ret


def test_pass_high_spades_if_no_lower():
    # Test the Ace of Spades gets returned
    cards = deserialize(["2C", "4C", "AS", "KD", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2D", "3H"])
    suits = split_into_suits(cards)
    ret = Rules._pass_high_spades_if_no_lower(suits)
    assert ret == CARD_AS

    # Test the King of Spades gets returned
    cards = deserialize(["2C", "4C", "KS", "KD", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2D", "3H"])
    suits = split_into_suits(cards)
    ret = Rules._pass_high_spades_if_no_lower(suits)
    assert ret == CARD_KS

    # Test the Queen of Spades gets returned
    cards = deserialize(["2C", "4C", "QS", "KD", "7C", "6C", "5H", "8H", "3D", "6D", "JD", "2D", "3H"])
    suits = split_into_suits(cards)
    ret = Rules._pass_high_spades_if_no_lower(suits)
    assert ret == CARD_QS

    # Test no Spades get returned if we have lower Spades
    cards = deserialize(["2C", "4C", "JS", "QS", "XS", "AS", "KC", "3D", "6D", "AH", "2S", "6S", "7S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_high_spades_if_no_lower(suits)
    assert not ret


def test_pass_high_except_spades():
    # Test a Club is returned
    cards = deserialize(["XS", "3H", "4H", "JC", "6H", "2D", "JH", "6D", "XD", "JD", "QD", "3S", "5S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_high_except_spades(suits)
    assert ret == deserialize("JC")

    # Test a Diamond is returned
    cards = deserialize(["8S", "JS", "QS", "6C", "9C", "2H", "4H", "JD", "QH", "7C", "6D", "QD", "KH"])
    suits = split_into_suits(cards)
    ret = Rules._pass_high_except_spades(suits)
    assert ret == deserialize("QD")

    # Test a Heart is returned
    cards = deserialize(["2C", "6C", "AS", "3H", "AC", "3D", "XH", "JH", "7D", "KH", "AH", "KD", "3S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_high_except_spades(suits)
    assert ret == deserialize("AH")


def test_pass_smallest_suit_except_spades():
    # Test a Club is returned
    cards = deserialize(["7C", "2H", "AC", "3D", "JH", "6D", "AH", "9D", "JD", "QD", "AD", "6S", "7S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_smallest_suit_except_spades(suits)
    assert ret == deserialize("AC")

    # Test a Diamond is returned
    cards = deserialize(["3C", "KS", "7C", "XC", "6H", "AC", "2D", "9H", "5D", "QH", "6D", "AH", "3S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_smallest_suit_except_spades(suits)
    assert ret == deserialize("6D")

    # Test a Heart is returned
    cards = deserialize(["2C", "3C", "4C", "7C", "8C", "QC", "AC", "XH", "JH", "6D", "QD", "AD", "5S"])
    suits = split_into_suits(cards)
    ret = Rules._pass_smallest_suit_except_spades(suits)
    assert ret == deserialize("JH")
