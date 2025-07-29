This package provides functionality to compute semivalues and related concepts. The most prominent example of a semivalue is the Shapley value.

Broad Functionality:
- Compute Shapley value exact or approximately
- Compute decomposition matrices based on the Shapley value

Detailed Functionality:
- Compute Shapley value (exact and approximately)
- Compute Shapley value decomposition by size (exact and approximately) (_n x n_ matrix where each entry is aggregated over the respective subset size)
- Compute [Shapley value of a player to another player](https://link.springer.com/content/pdf/10.1007/s003550000070.pdf) (exact and approximately) (_Hausken, Kjell, and Matthias Mohr. "The value of a player in n-person games." Social Choice and Welfare 18 (2001): 465-483._)

For the approximation methods of the Shapley value we refer to https://arxiv.org/pdf/1306.4265

## How To Use
You need to have a utility function mapping an arbitrary set of players to a real number. Players names should be {0, ..., n-1}, i.e. the utility function should return values for all subsets of {0, ..., n-1}.
```python
def utility_game_function(S):
    ...
    return result

from semivalues import shapley

num_players = 3

# Exact computation (n-vector)
shapley.exact(utility_game_function=utility_game_function, num_players=num_players)
# Sampled computation (n-vector)
shapley.strata_sampling(utility_game_function=utility_game_function, num_players=num_players, num_samples=100000)

from semivalues.decompositions.shapley import by_size
from semivalues.decompositions.shapley import player_to_player
# Exact computation (n x n matrix)
by_size.exact(utility_game_function=utility_game_function, num_players=num_players)
player_to_player.exact(utility_game_function=utility_game_function, num_players=num_players)
# Sampled computation (n x n matrix)
by_size.monte_carlo_sampling(utility_game_function=utility_game_function, num_players=num_players, num_samples=100000)
player_to_player.monte_carlo_sampling(utility_game_function=utility_game_function, num_players=num_players, num_samples=100000)
```