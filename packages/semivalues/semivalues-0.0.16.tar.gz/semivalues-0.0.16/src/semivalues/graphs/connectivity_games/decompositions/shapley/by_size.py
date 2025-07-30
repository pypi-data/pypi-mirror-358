import math
from typing import Callable

import numpy as np

from semivalues.graphs.connectivity_games.decompositions.skibski_algorithm import skibski_decomposed_by_size_in_place


def exact(utility_game_function: Callable, n: int, G):
    shapley_values = np.zeros((n, n))
    weights = {len_S: math.factorial(len_S - 1) * math.factorial(n - len_S) / math.factorial(n) for len_S in range(1, n+1)}
    skibski_decomposed_by_size_in_place(G, n, shapley_values, utility_game_function, weights)
    return shapley_values
