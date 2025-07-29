import numpy as np
import random

from semivalues import shapley

random.seed(1)


def test_exact_player_to_player_decomposition(game_utility_u):
    result_matrix = shapley.exact(game_utility_u, 3)
    assert (np.allclose(result_matrix, [390, 30, 120]))

def test_approx_player_to_player_decomposition(game_utility_u):

    relative_tolerance = 0.05
    approx_array = shapley.strata_sampling(game_utility_u, 3, num_samples=100000)
    expected = np.array([390, 30, 120])

    is_within_tolerance = np.abs(expected - approx_array) <= relative_tolerance * np.abs(expected)
    assert np.all(is_within_tolerance)
