import numpy as np
import random

from semivalues import banzhaf

from tests.utils import measure_runtime_and_log_to_csv

random.seed(1)


def test_exact_banzhaf(game_utility_u):
    result_array = banzhaf.exact(game_utility_u, 3)
    assert (np.allclose(result_array, [405, 45, 135]))


@measure_runtime_and_log_to_csv(implementation_type="python")
def test_approx_banzhaf(game_utility_u):
    relative_tolerance = 0.05
    approx_array = banzhaf.sampling(game_utility_u, 3, num_samples=100000)
    print(approx_array)
    expected = np.array([405, 45, 135])

    is_within_tolerance = np.abs(expected - approx_array) <= relative_tolerance * np.abs(expected)
    assert np.all(is_within_tolerance)
