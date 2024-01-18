import pytest

from utils import ranking


@pytest.mark.parametrize(
    "points,rankings",
    [
        ([75, 98, 102, 89], [0, 2, 3, 1]),
    ],
)
def test_ranking(points, rankings):
    assert [ranking(v, points) for v in points] == rankings
