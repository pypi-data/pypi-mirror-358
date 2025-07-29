import random

import numpy as np

from semivalues.decompositions.shapley import player_to_player

from tests.conftest import game_utility_u

random.seed(1)

def test_exact_player_to_player_decomposition(game_utility_u):
    expected_matrix = [
        [295, 25, 70],
        [25, 25, -20],
        [70, -20, 70]
    ]
    result_matrix = player_to_player.exact(game_utility_u, 3)
    assert np.allclose(result_matrix, expected_matrix)

def test_approx_player_to_player_decomposition(game_utility_u):
    expected = np.array([
        [295, 25, 70],
        [25, 25, -20],
        [70, -20, 70]
    ])
    approx = player_to_player.monte_carlo_sampling(game_utility_u, 3, symmetric=True, num_samples=100000)
    relative_tolerance = 0.05
    is_within_tolerance = np.abs(expected - approx) <= relative_tolerance * np.abs(expected)
    assert np.all(is_within_tolerance)
