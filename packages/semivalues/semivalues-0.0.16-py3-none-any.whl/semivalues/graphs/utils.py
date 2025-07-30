def create_adjacency_list(vertices, edges):
    adjacency_list = {v: set() for v in vertices}
    for u, v in edges:
        adjacency_list[u].add(v)
        adjacency_list[v].add(u)  # undirected
    return adjacency_list
