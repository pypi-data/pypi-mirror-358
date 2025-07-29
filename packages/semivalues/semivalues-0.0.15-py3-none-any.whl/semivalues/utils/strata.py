import random
from typing import Callable

import numpy as np
from tqdm import tqdm


def distribute_budget_to_players(n, num_samples):
    m = [int(num_samples / n)] * n
    rest_player_budget = num_samples % n
    for i in range(rest_player_budget):
        m[i] += 1
    return m


def stratify_of_subset(n, m, utility_game_function: Callable, shapley_values_k, c_i_l):
    # budget per stratum -> budget is the matrix m_i_l
    budget = np.zeros(shape=(n, n), dtype=np.int64)
    denominator = np.sum([np.power(k + 1, 2 / 3) for k in range(n)])

    for i in range(n):
        for l in range(n):
            budget[i][l] = int((m[i] * np.power(l + 1, 2 / 3)) / denominator)

    for i in range(n):
        left = int(m[i] - sum(budget[i]))
        for j in range(left):
            budget[i][j] += 1

    # calculate the strata available for each player
    available_stratum = [[i for i in range(n)] for _ in range(n)]
    for i in range(len(available_stratum)):
        for j in range(len(available_stratum[i])):
            if budget[i][j] == 0:
                available_stratum[i].remove(j)


    # sample coalitions
    for active_player in tqdm(range(n)):
        S_i_l = list(range(n))
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

