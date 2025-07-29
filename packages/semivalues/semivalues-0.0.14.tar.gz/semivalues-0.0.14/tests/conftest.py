import pytest

# Example from paper: https://link.springer.com/content/pdf/10.1007/s003550000070.pdf
GAME_VALUES = {
    frozenset(): 0,
    frozenset({0}): 180,
    frozenset({1}): 0,
    frozenset({2}): 0,
    frozenset({1, 2}): 0,
    frozenset({0, 1}): 360,
    frozenset({0, 2}): 540,
    frozenset({0, 1, 2}): 540,
}


@pytest.fixture
def game_utility_u() -> callable:
    """A pytest fixture that provides the characteristic function for the game."""
    def u(coalition: set) -> int:
        return GAME_VALUES[frozenset(coalition)]
    return u