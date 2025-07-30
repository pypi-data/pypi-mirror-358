from typing import Callable

import numpy as np

from semivalues.graphs.connectivity_games.decompositions.shapley.by_size import skibski_decomposed_by_size_in_place


def exact(utility_game_function: Callable, n: int, G):
    banzhaf_values = np.zeros((n, n))
    norm_factor = (1 / (2 ** (n - 1)))
    weights = {len_S: norm_factor for len_S in range(1, n + 1)}
    skibski_decomposed_by_size_in_place(G, n, banzhaf_values, utility_game_function, weights)
    return banzhaf_values
