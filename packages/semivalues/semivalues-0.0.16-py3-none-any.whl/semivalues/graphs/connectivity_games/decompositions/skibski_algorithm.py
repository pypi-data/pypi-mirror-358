import math

from semivalues.graphs.connectivity_games.skibski_algorithm import GraphInfoObject, DFSEnumerateRec, CountingSet, \
    get_nodes_by_degree_desc
from semivalues.graphs.utils import create_adjacency_list


def skibski_decomposed_by_size_in_place(G, n, semivalues, utility_game_function, weights):
    adj_list = create_adjacency_list(G[0], G[1])
    adj_list = {node: list(adj_list[node]) for node in G[0]}
    label_dict = {i: i for i in range(n)}
    my_graph_obj = GraphInfoObject(G[0], G[1], adj_list, semivalues, utility_game_function, label_dict, weights)

    sorted_nodes = get_nodes_by_degree_desc(adj_list)
    position_lookup = {value: index for index, value in enumerate(sorted_nodes)}
    for node in my_graph_obj.adj_list:
        my_graph_obj.adj_list[node].sort(key=lambda x: position_lookup[x], reverse=True)

    for node in sorted_nodes:
        X = set()
        for pred_node in sorted_nodes:
            if pred_node == node:
                break
            X.add(pred_node)
        DFSEnumerateRec(my_graph_obj, [node], {node}, X, 0, set(), [math.inf], CountingSet())
