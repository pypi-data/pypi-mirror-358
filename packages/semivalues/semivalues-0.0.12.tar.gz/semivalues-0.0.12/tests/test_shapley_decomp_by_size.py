import random

import numpy as np

from semivalues.decompositions.shapley import by_size

from tests.conftest import game_utility_u

random.seed(1)

def test_exact_decomposition_by_size(game_utility_u):
    expected_matrix = [
        [60, 150, 180],
        [0, 30, 0],
        [0, 60, 60]
    ]
    result_matrix = by_size.exact(game_utility_u, 3)
    assert np.allclose(result_matrix, expected_matrix)

def test_approx_decomposition_by_size(game_utility_u):
    expected = np.array([
        [60, 150, 180],
        [0, 30, 0],
        [0, 60, 60]
    ])
    approx = by_size.monte_carlo_sampling(game_utility_u, 3, num_samples=10000)
    relative_tolerance = 0.05
    is_within_tolerance = np.abs(expected - approx) <= relative_tolerance * np.abs(expected)
    assert np.all(is_within_tolerance)
