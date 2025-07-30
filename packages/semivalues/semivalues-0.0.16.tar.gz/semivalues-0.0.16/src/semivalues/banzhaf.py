import itertools
import math
from typing import Callable, Set

import numpy as np
from tqdm import tqdm


def exact(utility_game_function: Callable, num_players: int):
    """
    Parameters:
    utility_game_function (Callable): Function which represents the game.
    n (int): number of players

    Returns:
    List[Float]: The computed shapley values
    """
    players = range(num_players)
    banzhaf_values = np.zeros(num_players)
    normalization_factor = 2 ** (num_players - 1)
    for player in tqdm(players):
        banzhaf_index_value = 0
        for subset in itertools.chain.from_iterable(itertools.combinations(players, r) for r in range(num_players + 1)):
            if player not in subset:
                subset_with_player = set(subset).union({player})
                marginal_contribution = utility_game_function(subset_with_player) - utility_game_function(set(subset))
                banzhaf_index_value += marginal_contribution
        banzhaf_values[player] = banzhaf_index_value / normalization_factor
    return banzhaf_values


def sampling(utility_game_function: Callable[[Set[int]], float], num_players: int, num_samples=100000):
    num_permutations = round(num_samples / num_players)

    weight_array = np.zeros(num_players, dtype=np.object_)
    for i in range(num_players):
        weight_array[i] = (num_players * math.comb(num_players - 1, i)) / (2 ** (num_players - 1))
    banzhaf_values = np.zeros(num_players)

    for _ in range(num_permutations):
        perm_sample = np.random.permutation(num_players)
        for i in range(num_players):
            pos = np.where(perm_sample == i)[0][0]
            S = set(perm_sample[:pos])
            marginal = utility_game_function(S.union({i})) - utility_game_function(S)
            banzhaf_values[i] += marginal * weight_array[len(S)]
    banzhaf_values = banzhaf_values / num_permutations
    return banzhaf_values
