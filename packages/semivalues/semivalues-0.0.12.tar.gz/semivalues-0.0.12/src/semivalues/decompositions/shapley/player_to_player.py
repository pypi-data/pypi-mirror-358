from typing import Callable, List, Set
import itertools
import math
import random

from tqdm import tqdm
import numpy as np

from semivalues.utils.weights import compute_weights


def exact(utility_game_function: Callable, num_players: int, symmetric=False):
    """
    Parameters:
    utility_game_function (Callable): Function which represents the game.
    n (int): number of players

    Returns:
    List[Float]: The computed shapley values
    """
    players = np.arange(num_players)
    shapley_values = np.zeros((num_players, num_players))

    factorials_vec = np.vectorize(math.factorial, otypes=["int64"])
    factorials = factorials_vec(np.arange(num_players + 1))
    weights = compute_weights(factorials, num_players)
    weights = np.append([1], weights)

    indices = np.arange(1, num_players + 1)
    cumulative_harmonics = np.cumsum(1 / indices[::-1])[::-1]
    harmonic_sums = np.append([0], cumulative_harmonics)

    utility_cache = {}

    for player_i in tqdm(players):
        if symmetric:
            players_to_iterate = range(player_i, num_players)
        else:
            players_to_iterate = players
        for player_j in players_to_iterate:
            sum_ij = 0
            for subset in itertools.chain.from_iterable(itertools.combinations(players, r) for r in range(num_players + 1)):
                subset_size = len(subset)

                utility_full = get_or_compute_utility(subset, [], utility_game_function, utility_cache)
                utility_without_i = get_or_compute_utility(subset, [player_i], utility_game_function, utility_cache)
                utility_without_j = get_or_compute_utility(subset, [player_j], utility_game_function, utility_cache)
                utility_without_i_and_j = get_or_compute_utility(subset, [player_i, player_j], utility_game_function, utility_cache)

                adapted_marginal_contribution = utility_full - utility_without_i - utility_without_j + utility_without_i_and_j

                sum_ij += weights[subset_size] * adapted_marginal_contribution * harmonic_sums[subset_size]
            shapley_values[player_i, player_j] = sum_ij

    if symmetric:
        # Mirror the upper triangular part to the lower triangular part
        i_upper = np.triu_indices(num_players, k=1)  # Get the indices of the upper triangular part excluding diagonal
        shapley_values[(i_upper[1], i_upper[0])] = shapley_values[i_upper]  # Mirror to the lower triangular part

    return shapley_values


def get_set_without_players(S, players: list):
    subset_without_players = S.copy()
    for player in players:
        subset_without_players.discard(player)
    return subset_without_players


def get_or_compute_utility(subset, players_to_exclude, utility_game_function, utility_cache):
    subset_key = tuple(get_set_without_players(set(subset), players_to_exclude))
    if subset_key not in utility_cache:
        utility_cache[subset_key] = utility_game_function(set(subset_key))
    return utility_cache[subset_key]


def monte_carlo_sampling(
        utility_game_function: Callable,
        num_players: int,
        symmetric=False,
        num_samples: int = 100000
) -> np.ndarray:
    """
    Parameters:
    utility_game_function (Callable): Function which represents the game.
    n (int): number of players
    symmetric (Boolean): Boolean if the resulting matrix will be symmetric by the property of the game.
    num_samples: (int): number of samples

    Returns:
    List[Float]: The computed shapley values
    """
    players = np.arange(num_players)
    shapley_values = np.zeros((num_players, num_players))

    factorials_vec = np.vectorize(math.factorial, otypes=["int64"])
    factorials = factorials_vec(np.arange(num_players + 1))
    weights = compute_weights(factorials, num_players)
    weights = np.append([1], weights)

    indices = np.arange(1, num_players + 1)
    cumulative_harmonics = np.cumsum(1 / indices[::-1])[::-1]
    harmonic_sums = np.append([0], cumulative_harmonics)

    utility_cache = {}

    for player_i in tqdm(players):
        if symmetric:
            players_to_iterate = range(player_i, num_players)
        else:
            players_to_iterate = players
        for player_j in players_to_iterate:
            sum_ij = 0
            num_samples_entry = math.floor(num_samples / num_players ** 2)
            for _ in range(num_samples_entry):
                bitmask = random.randint(0, 2 ** num_players - 1)  # Random integer in range [0, 2^n -1]
                subset = {i for i in range(num_players + 1) if bitmask & (1 << i)}  # Convert bitmask to subset

                subset_size = len(subset)

                utility_full = get_or_compute_utility(subset, [], utility_game_function, utility_cache)
                utility_without_i = get_or_compute_utility(subset, [player_i], utility_game_function, utility_cache)
                utility_without_j = get_or_compute_utility(subset, [player_j], utility_game_function, utility_cache)
                utility_without_i_and_j = get_or_compute_utility(subset, [player_i, player_j], utility_game_function, utility_cache)

                adapted_marginal_contribution = utility_full - utility_without_i - utility_without_j + utility_without_i_and_j

                sum_ij += weights[subset_size] * adapted_marginal_contribution * harmonic_sums[subset_size]
            shapley_values[player_i, player_j] = sum_ij / num_samples_entry
    if symmetric:
        # Mirror the upper triangular part to the lower triangular part
        i_upper = np.triu_indices(num_players, k=1)  # Get the indices of the upper triangular part excluding diagonal
        shapley_values[(i_upper[1], i_upper[0])] = shapley_values[i_upper]  # Mirror to the lower triangular part
    return shapley_values * 2 ** num_players
