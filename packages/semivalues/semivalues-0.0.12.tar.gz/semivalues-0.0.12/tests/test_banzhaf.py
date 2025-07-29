import numpy as np
import random

from semivalues import banzhaf

random.seed(1)


def test_exact_player_to_player_decomposition(game_utility_u):
    result_matrix = banzhaf.exact(game_utility_u, 3)
    assert (np.allclose(result_matrix, [405, 45, 135]))

def test_approx_player_to_player_decomposition(game_utility_u):

    relative_tolerance = 0.05
    approx_array = banzhaf.sampling(game_utility_u, 3, num_samples=100000)
    print(approx_array)
    expected = np.array([405, 45, 135])

    is_within_tolerance = np.abs(expected - approx_array) <= relative_tolerance * np.abs(expected)
    assert np.all(is_within_tolerance)
