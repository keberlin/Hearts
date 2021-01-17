import pytest

from rules import Rules

#pytest_plugins = ["tests.fixtures.player"]

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
def test_score(cards, avail, score):
    ret = Rules._score(cards, avail)
    assert ret == score
