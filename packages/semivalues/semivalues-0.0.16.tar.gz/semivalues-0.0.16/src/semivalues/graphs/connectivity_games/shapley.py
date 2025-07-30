import math
from typing import Callable
from typing import Tuple, Set

import networkx as nx
import numpy as np

from semivalues.graphs.connectivity_games.skibski_algorithm import skibski_in_place


def shapley_value_skibski(utility_game_function: Callable, n: int, G: Tuple[Set[int], Set[Tuple[int, int]]]):
    shapley_values = np.zeros(n)
    weights = {len_S: math.factorial(len_S - 1) * math.factorial(n - len_S) / math.factorial(n) for len_S in range(1, n+1)}
    skibski_in_place(G, n, shapley_values, utility_game_function, weights)
    return shapley_values


def exact(utility_game_function: Callable, n: int, G: nx.Graph):
    G_set = (set(G.nodes), set(G.edges))
    return shapley_value_skibski(utility_game_function, n, G_set)
