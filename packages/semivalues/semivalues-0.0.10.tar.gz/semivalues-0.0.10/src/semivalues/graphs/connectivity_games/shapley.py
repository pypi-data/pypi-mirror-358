from typing import Callable

import networkx as nx
from semivalues import shapley


def exact(utility_game_function: Callable, n: int, G: nx.Graph):
    return shapley.exact(utility_game_function, n)
