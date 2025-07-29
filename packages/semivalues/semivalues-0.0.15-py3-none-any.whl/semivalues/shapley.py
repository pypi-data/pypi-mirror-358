import itertools
from typing import Callable

import numpy as np
from scipy.special import factorial
from tqdm import tqdm

from .utils.weights import compute_weights
from .utils.strata import distribute_budget_to_players, stratify_of_subset


def exact(utility_game_function: Callable, num_players: int):
    """
    Parameters:
    utility_game_function (Callable): Function which represents the game.
    n (int): number of players

    Returns:
    List[Float]: The computed shapley values
    """
    players = np.arange(num_players)
    shapley_values = np.zeros(num_players)

    factorials = factorial(np.arange(num_players + 1), exact=True)
    weights = compute_weights(factorials, num_players)
    utility_cache = {}

    print(f"Progress bar: Computing Shapley Value for {num_players} players:")
    for player in tqdm(players):
        shapley_value_player = 0
        for subset in itertools.chain.from_iterable(itertools.combinations(players, r) for r in range(num_players + 1)):
            if player not in subset:
                subset_with_player = subset + (player,)

                if subset not in utility_cache:
                    utility_cache[subset] = utility_game_function(set(subset))
                if subset_with_player not in utility_cache:
                    utility_cache[subset_with_player] = utility_game_function(set(subset_with_player))
                marginal_contribution = utility_cache[subset_with_player] - utility_cache[subset]

                shapley_value_player += weights[len(subset)] * marginal_contribution

        # shapley_values[player] = round(shapley_value_player, 3)  # ROUNDING NEEDED FOR NUMERICAL ERRORS as the weight can be imprecise numbers!
        shapley_values[player] = shapley_value_player
    return shapley_values



# implementation of algorithm2 from here: https://arxiv.org/pdf/1306.4265
# inspired by: https://github.com/kolpaczki/Approximating-the-Shapley-Value-without-Marginal-Contributions/blob/main/ApproxMethods/StratifiedSampling/StratifiedSampling.py#L69
def strata_sampling(utility_game_function: Callable, num_players: int, num_samples=100000):
    shapley_values_k = np.zeros((num_players, num_players))
    c_i_l = np.zeros((num_players, num_players))

    # distribute budget among players -> m is list of each player's budget
    m = distribute_budget_to_players(num_players, num_samples)

    # stratify_by_size_of_subset(n, m, u, shapley_values_k, c_i_l)
    stratify_of_subset(num_players, m, utility_game_function, shapley_values_k, c_i_l)
    shapley_values = 1 / np.sum(np.where(c_i_l > 0, 1, 0), axis=1) * np.sum(shapley_values_k, axis=1)
    shapley_values = [val for val in shapley_values]
    return shapley_values
