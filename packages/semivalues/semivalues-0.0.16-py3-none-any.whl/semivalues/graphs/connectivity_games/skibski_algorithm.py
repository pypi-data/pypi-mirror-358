import copy
import math

from semivalues.graphs.utils import create_adjacency_list


class GraphInfoObject:
    def __init__(self, V, E, adj_list, shapley_values, u, label_dict, weights):
        self.V = V
        self.E = E
        self.adj_list = adj_list  # Adjacency list
        self.shapley_values = shapley_values
        self.game = u
        self.weights = weights
        self.label_dict = label_dict

class CountingSet:
    def __init__(self):
        self.counts = {}

    def add(self, element):
        if element in self.counts:
            self.counts[element] += 1
        else:
            self.counts[element] = 1

    def get_counts(self, element):
        return self.counts.get(element, 0)

    def remove(self, element):
        # Remove one occurrence of the element if it exists
        if element in self.counts:
            if self.counts[element] > 1:
                self.counts[element] -= 1
            else:
                del self.counts[element]
        else:
            raise KeyError(f"Element {element} not found in the set.")


def get_nodes_by_degree_desc(input_dict, adj_list, my_graph_obj):
    sorted_list = sorted(input_dict.keys(), key=lambda k: len(input_dict[k]), reverse=True)
    return sorted_list


def DFSEnumerateRec(my_graph_obj, path, S, X, startIt, neighbors, low, SC):
    v = path[-1]
    l = low[-1]
    for i in range(startIt, len(my_graph_obj.adj_list[v])):
        u = my_graph_obj.adj_list[v][i]
        if u not in S and u not in X:
            X_copy = copy.copy(X)
            neighbors_copy = copy.copy(neighbors)
            SC_copy = copy.copy(SC)
            DFSEnumerateRec(my_graph_obj, path + [u], S.union({u}), X_copy, 0, neighbors_copy, low + [math.inf], SC_copy)
            X.add(u)
            neighbors.add(u)
        elif u in X:
            neighbors.add(u)
        elif u in set(path) and path.index(u) < low[-1]: # WAR SO NICHT IN PSEUDOCODE
            l = path.index(u)
            low[-1] = l

    path.pop()
    low.pop()
    if len(path) > 0:
        w = path[-1]
        if l >= len(path):
            SC.add(w)
        elif l < low[-1]:
            low[-1] = l
        startIt = my_graph_obj.adj_list[w].index(v) + 1
        DFSEnumerateRec(my_graph_obj, path, S, X, startIt, neighbors, low, SC)
    else:
        G = (my_graph_obj.V, my_graph_obj.E)
        if SC.get_counts(v) == 1:
            SC.remove(v)
        for i in SC.counts:
            my_graph_obj.shapley_values[i] += my_graph_obj.weights[len(S)] * my_graph_obj.game(S=S, G=G, label_dict=my_graph_obj.label_dict)
        for i in S.difference(SC.counts):
            S_without_i = copy.copy(S)
            S_without_i.remove(i)
            my_graph_obj.shapley_values[i] += my_graph_obj.weights[len(S)] * \
                                             (my_graph_obj.game(S=S, G=G, label_dict=my_graph_obj.label_dict)
                                              - my_graph_obj.game(S=S_without_i, G=G, label_dict=my_graph_obj.label_dict)
                                              )
        for i in my_graph_obj.V.difference(S.union(neighbors)):
            my_graph_obj.shapley_values[i] -= my_graph_obj.weights[len(S)+1] * my_graph_obj.game(S=S, G=G, label_dict=my_graph_obj.label_dict)



def skibski_in_place(G, n, shapley_values, utility_game_function, weights):

    adj_list = create_adjacency_list(G[0], G[1])
    adj_list = {node: list(adj_list[node]) for node in G[0]}
    label_dict = {i: i for i in range(n)}
    my_graph_obj = GraphInfoObject(G[0], G[1], adj_list, shapley_values, utility_game_function, label_dict, weights)

    def get_nodes_by_degree_desc(input_dict):
        sorted_list = sorted(input_dict.keys(), key=lambda k: len(input_dict[k]), reverse=True)
        return sorted_list
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

