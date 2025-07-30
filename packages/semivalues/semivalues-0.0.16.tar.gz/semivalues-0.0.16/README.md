<p align="center">
  <img src="https://raw.githubusercontent.com/SimonGlomb/Metadata/dfcd6ac77dcc40e1e6562ce2b35c62114f1d3a95/logo.svg" width="200">
</p>

This package offers tools for computing semivalues, with the Shapley value being the most prominent example. 
The functionality extends to computational tools for graph-based games.

Broad Functionality:
- Computing the Shapley/Banzhaf value exact or approximately
- Computing decomposition matrices

Detailed Functionality:
- Computing the Shapley/Banzhaf value (exact and approximately)
- Computing the Shapley/Banzhaf value decomposition by size (exact and approximately) (_n x n_ matrix where each entry is aggregated over the respective subset size)
- Computing the [Shapley value of a player to another player](https://link.springer.com/content/pdf/10.1007/s003550000070.pdf) (exact and approximately) (_Hausken, Kjell, and Matthias Mohr. "The value of a player in n-person games." Social Choice and Welfare 18 (2001): 465-483._)

For the approximation methods of the Shapley value we refer to https://arxiv.org/pdf/1306.4265

## How To Use
You need to have a utility function mapping an arbitrary set of players to a real number. Players names should be {0, ..., n-1}, i.e. the utility function should return values for all subsets of {0, ..., n-1}.
We will use the example introduced [here](https://link.springer.com/content/pdf/10.1007/s003550000070.pdf)

```python
def utility_game_function(S):
    GAME_VALUES = {
        frozenset(): 0,
        frozenset({0}): 180,
        frozenset({1}): 0,
        frozenset({2}): 0,
        frozenset({1, 2}): 0,
        frozenset({0, 1}): 360,
        frozenset({0, 2}): 540,
        frozenset({0, 1, 2}): 540,
    }

    def game_utility(coalition: set) -> int:
        return GAME_VALUES.get(frozenset(coalition), 0)

    return game_utility(S)


num_players = 3

from semivalues import shapley, banzhaf

# (n-vector)
shapley.exact(utility_game_function=utility_game_function, num_players=num_players)
shapley.strata_sampling(utility_game_function=utility_game_function, num_players=num_players, num_samples=100000)

banzhaf.exact(utility_game_function=utility_game_function, num_players=num_players)
banzhaf.sampling(utility_game_function=utility_game_function, num_players=num_players, num_samples=100000)

from semivalues.decompositions.by_size import shapley as shapley_by_size
from semivalues.decompositions.by_size import banzhaf as banzhaf_by_size

# (n x n matrix)
shapley_by_size.exact(utility_game_function=utility_game_function, num_players=num_players)
shapley_by_size.strata_sampling(utility_game_function=utility_game_function, num_players=num_players, num_samples=100000)

from semivalues.decompositions.by_size import banzhaf, shapley

# (n x n matrix)
banzhaf_by_size.exact(utility_game_function=utility_game_function, num_players=num_players)
banzhaf_by_size.monte_carlo_sampling(utility_game_function=utility_game_function, num_players=num_players, num_samples=100000)

from semivalues.decompositions.player_to_player import shapley as shapley_player_to_player

# (n x n matrix)
shapley_player_to_player.exact(utility_game_function=utility_game_function, num_players=num_players)
shapley_player_to_player.monte_carlo_sampling(utility_game_function=utility_game_function, num_players=num_players,
                                      num_samples=100000)
```