import math
import random
from math import inf
from typing import Callable
import itertools

import numpy as np
from semivalues.utils.weights import compute_weights
from tqdm import tqdm

from scipy.special import factorial


def exact(utility_game_function: Callable, num_players: int):
    """
    Parameters:
    utility_game_function (Callable): Function which represents the game.
    n (int): number of players

    Returns:
    List[Float]: The computed shapley values
    """
    players = range(num_players)
    banzhaf_values = np.zeros((num_players, num_players))
    normalization_factor = 2 ** (num_players - 1)
    for player in tqdm(players, desc="Calculating Decomposition by Size values"):
        for subset in itertools.chain.from_iterable(itertools.combinations(players, r) for r in range(num_players + 1)):
            if player not in subset:
                subset_with_player = set(subset).union({player})
                marginal_contribution = utility_game_function(subset_with_player) - utility_game_function(set(subset))

                banzhaf_values[player, len(subset)] += marginal_contribution
        for i in range(len(players)):
            banzhaf_values[player, i] = banzhaf_values[player, i] / normalization_factor
    return banzhaf_values


def monte_carlo_sampling(utility_game_function: Callable, num_players: int, num_samples=100000):
    num_permutations = round(num_samples / num_players)

    weight_array = np.zeros(num_players, dtype=np.object_)
    for i in range(num_players):
        weight_array[i] = (num_players * math.comb(num_players - 1, i)) / (2 ** (num_players - 1))
    banzhaf_values = np.zeros((num_players, num_players))

    for _ in tqdm(range(num_permutations), desc="Calculating Monte Carlo interaction values"):
        perm_sample = np.random.permutation(num_players)
        for i in range(num_players):
            pos = np.where(perm_sample == i)[0][0]
            S = set(perm_sample[:pos])
            marginal = utility_game_function(S.union({i})) - utility_game_function(S)
            banzhaf_values[i][len(S)] += marginal * weight_array[len(S)]
    banzhaf_values = banzhaf_values / num_permutations
    return banzhaf_values
