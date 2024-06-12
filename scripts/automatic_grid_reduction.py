import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations

def generate_grid_graph(n, m):
    G = nx.grid_2d_graph(n, m)
    mapping = {(i, j): f"[l{i * m + j}]" for i in range(n) for j in range(m)}
    G = nx.relabel_nodes(G, mapping)
    return G


def import_graph():
    df = pd.read_csv('case_studies/stylized_eu/inputs/transmission_lines.csv')
    return nx.from_pandas_edgelist(df, 'from', 'to')


def plot_graph(G):
    plt.figure(1, figsize=(10, 10))
    nx.draw(G, with_labels=True, node_size=700, node_color='lightblue', font_weight='bold', font_size=10)
    plt.show()


def get_num_individuals(node):
    # split the node identifier by commas and count the elements
    return len(node.split(','))


def get_total_num_individuals(clique):
    # for each clique node, find the number of individuals and sum those
    return sum([get_num_individuals(node) for node in clique])


def find_cycle(G, v, visited, path, length):
    if len(path) > length:
        return None
    if len(path) == length:
        if path[0] in G.neighbors(v):
            return path
        return None

    for neighbor in G.neighbors(v):
        if neighbor not in visited:
            visited.add(neighbor)
            result = find_cycle(G, neighbor, visited, path + [neighbor], length)
            if result:
                return result
            visited.remove(neighbor)
    return None


def merge(G, path):
    new_node_id = f"[{','.join([str(n) for n in path])}]"
    to_connect = {node for v in path for node in G.neighbors(v)} - set(path)
    G.remove_nodes_from(path)
    G.add_node(new_node_id)
    G.add_edges_from([(new_node_id, node) for node in to_connect])


def chain_reduce(G):
    found_parts = []
    deg_1_nodes = [node for node, degree in G.degree() if degree == 1]
    # make sure composed nodes with fewer individuals are considered first
    deg_1_nodes = sorted(deg_1_nodes, key=get_num_individuals)
    while len(deg_1_nodes) > 0:
        chain = []
        v = deg_1_nodes[0]
        while v is not None:
            chain.append(v)
            # walk the chain
            neighbors = [n for n in G.neighbors(v) if G.degree(n) <= 2 and n not in chain]
            v = neighbors[0] if len(neighbors) == 1 else None
        # subdivide the chain into pairs of nodes to merge
        for idx in range(1, len(chain), 2):
            part = chain[idx-1:idx+1]
            found_parts.append(part)
        deg_1_nodes = [n for n in deg_1_nodes if n not in chain]
    return found_parts


def grid_reduce(G, k=4):
    found_grids = []
    G_ = G.copy()
    while G_.number_of_nodes() > 0:
        # make sure composed nodes with fewer individuals are considered first
        sorted_nodes = sorted(G_.nodes(), key=get_num_individuals)
        v = list(sorted_nodes)[0]
        cycle = find_cycle(G_, v, set([v]), [v], k)
        if cycle is not None:
            found_grids.append(cycle)
            G_.remove_nodes_from(cycle[1:])
        G_.remove_node(v)
    return found_grids


def clique_reduce(G, max_clique_size):
    found_cliques = []
    nodes_used = set()
    all_cliques = list(nx.find_cliques(G))
    # find disjoint cliques of size k >= 3, starting with the biggest
    for i in range(max_clique_size-2):
        k = max_clique_size - i
        cliques = [clique for clique in all_cliques if len(clique) == k]
        # make sure cliques with fewer individuals are considered first
        cliques = sorted(cliques, key=get_total_num_individuals)
        for clique in cliques:
            # make sure the clique is disjoint from earlier discovered cliques
            if not any(node in nodes_used for node in clique):
                found_cliques.append(clique)
                nodes_used.update(clique)
    return found_cliques


def combined_reduce(G, max_clique_size):
    # keep working copy of graph
    G_ = G.copy()

    # find chains
    found_chain_parts = chain_reduce(G_)
    for chain_part in found_chain_parts:
        merge(G, chain_part)
        G_.remove_nodes_from(chain_part)

    # find grids
    found_grids = grid_reduce(G_)
    for grid in found_grids:
        merge(G, grid)
        G_.remove_nodes_from(grid)

    # find cliques
    found_cliques = clique_reduce(G_, max_clique_size)
    for clique in found_cliques:
        merge(G, clique)
        G_.remove_nodes_from(clique)


def combined_reduce_2(G, max_clique_size):
    # keep working copy of graph
    G_ = G.copy()

    # find cliques
    found_cliques = clique_reduce(G_, max_clique_size)
    for clique in found_cliques:
        merge(G, clique)
        G_.remove_nodes_from(clique)

    # find chains
    found_chain_parts = chain_reduce(G_)
    for chain_part in found_chain_parts:
        merge(G, chain_part)
        G_.remove_nodes_from(chain_part)

    # find grids
    found_grids = grid_reduce(G_)
    for grid in found_grids:
        merge(G, grid)
        G_.remove_nodes_from(grid)


# Generate and plot the grid graph
# Define the dimensions of the grid
# n = 6  # number of rows
# m = 8  # number of columns
# G = generate_grid_graph(n, m)


# Import a graph
G = import_graph()

# Plot the initial graph
plot_graph(G)


for i in range(2):
    combined_reduce_2(G, 8)
    plot_graph(G)