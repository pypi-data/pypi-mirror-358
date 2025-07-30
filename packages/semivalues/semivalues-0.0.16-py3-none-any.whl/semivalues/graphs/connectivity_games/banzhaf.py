from typing import Callable

import networkx as nx
import numpy as np

from semivalues.graphs.connectivity_games.shapley import skibski_in_place


def banzhaf_value_skibski(utility_game_function: Callable, n: int, G):
    shapley_values = np.zeros(n)
    norm_factor = (1 / (2 ** (n - 1)))
    weights = {len_S: norm_factor for len_S in range(1, n+1)}
    skibski_in_place(G, n, shapley_values, utility_game_function, weights)
    return shapley_values


def exact(utility_game_function: Callable, n: int, G: nx.Graph):
    G_set = (set(G.nodes), set(G.edges))
    return banzhaf_value_skibski(utility_game_function, n, G_set)
