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
    players = np.arange(num_players)
    shapley_values = np.zeros((num_players, num_players))

    # Calculate factorials beforehand for efficiency
    factorials = factorial(np.arange(num_players + 1), exact=True)
    weights = compute_weights(factorials, num_players)
    utility_cache = {}

    print(f"Progress bar: Computing Shapley Value for {num_players} players:")
    for player in tqdm(players):
        for subset in itertools.chain.from_iterable(itertools.combinations(players, r) for r in range(num_players + 1)):
            if player not in subset:
                subset_with_player = subset + (player,)

                if subset not in utility_cache:
                    utility_cache[subset] = utility_game_function(set(subset))
                if subset_with_player not in utility_cache:
                    utility_cache[subset_with_player] = utility_game_function(set(subset_with_player))
                marginal_contribution = utility_cache[subset_with_player] - utility_cache[subset]

                shapley_values[player, len(subset)] += marginal_contribution

        for i in range(len(players)):
            shapley_values[player, i] = shapley_values[player, i] * weights[i]
    return shapley_values

# implementation of algorithm2 from here: https://arxiv.org/pdf/1306.4265
# inspired by: https://github.com/kolpaczki/Approximating-the-Shapley-Value-without-Marginal-Contributions/blob/main/ApproxMethods/StratifiedSampling/StratifiedSampling.py#L69
def strata_sampling(utility_game_function: Callable, num_players: int, num_samples=100000):

    def distribute_budget_to_players(num_players, num_samples):
        # m = [int(num_samples / (2 * n))] * n
        m = [int(num_samples / num_players)] * num_players
        rest_player_budget = num_samples % num_players
        for i in range(rest_player_budget):
            m[i] += 1
        return m

    def stratify_of_subset(num_players, m, utility_game_function: Callable, shapley_values_k, c_i_l):
        # budget per stratum -> budget is the matrix m_i_l
        budget = np.zeros(shape=(num_players, num_players), dtype=np.int64)
        denominator = np.sum([np.power(k + 1, 2 / 3) for k in range(num_players)])

        for i in range(num_players):
            for l in range(num_players):
                budget[i][l] = int((m[i] * np.power(l + 1, 2 / 3)) / denominator)

        for i in range(num_players):
            left = int(m[i] - sum(budget[i]))
            for j in range(left):
                budget[i][j] += 1

        # calculate the strata available for each player
        available_stratum = [[i for i in range(num_players)] for _ in range(num_players)]
        for i in range(len(available_stratum)):
            for j in range(len(available_stratum[i])):
                if budget[i][j] == 0:
                    available_stratum[i].remove(j)

        # sample coalitions
        for active_player in tqdm(range(num_players)):
            S_i_l = list(range(num_players))
            S_i_l.remove(active_player)
            for stratum_size in available_stratum[active_player]:
                if stratum_size == 0:
                    for _ in range(budget[active_player][stratum_size]):
                        S1 = set()
                        S2 = {active_player}
                        delta_i_l = utility_game_function(S2) - utility_game_function(S1)
                        update_shapley_of_player(active_player, c_i_l, stratum_size, shapley_values_k, delta_i_l)
                    continue
                for _ in range(budget[active_player][stratum_size]):
                    # sample S
                    S1 = set(random.sample(S_i_l, stratum_size))
                    S2 = set(S1)
                    S2.add(active_player)
                    delta_i_l = utility_game_function(S2) - utility_game_function(S1)

                    # update shapley value
                    update_shapley_of_player(active_player, c_i_l, stratum_size, shapley_values_k, delta_i_l)

    def update_shapley_of_player(active_player, c_i_l, sampled_stratum, shapley_values_k, delta_i_l):
        c = c_i_l[active_player][sampled_stratum]
        shapley_values_k[active_player][sampled_stratum] = (shapley_values_k[active_player][sampled_stratum] * (c)
                                                            + delta_i_l) / (c + 1)
        c_i_l[active_player][sampled_stratum] += 1

    shapley_values_k = np.zeros((num_players, num_players))
    c_i_l = np.zeros((num_players, num_players))

    # distribute budget among players -> m is list of each player's budget
    m = distribute_budget_to_players(num_players, num_samples)

    # stratify_by_size_of_subset(n, m, u, shapley_values_k, c_i_l)
    stratify_of_subset(num_players, m, utility_game_function, shapley_values_k, c_i_l)

    # the times n is basically the same as the other, if we assume that each size gets at least one sample
    shapley_values_k_result = shapley_values_k / num_players
    shapley_values_k_result[shapley_values_k_result == inf] = 0

    return shapley_values_k_result
