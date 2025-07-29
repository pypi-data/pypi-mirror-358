from typing import Callable

import networkx as nx
from src.semivalues.decompositions.shapley import exact as exact_plain


def exact(utility_game_function: Callable, n: int, G: nx.Graph):
    return exact_plain(utility_game_function, n)
