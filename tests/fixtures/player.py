import pytest

from player_ai import AIPlayer


@pytest.fixture()
def player():
    player = AIPlayer(1)
    return player
