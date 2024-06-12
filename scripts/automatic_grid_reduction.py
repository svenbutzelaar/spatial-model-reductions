import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


# TODO: check combined node size, weighted search for loops, start at small nodes first

def generate_grid_graph(n, m):
    G = nx.grid_2d_graph(n, m)
    mapping = {(i, j): f"[l{i * m + j}]" for i in range(n) for j in range(m)}
    G = nx.relabel_nodes(G, mapping)
    return G


def import_graph():
    df = pd.read_csv("..\\case_studies\\9_9_star\\inputs\\transmission_lines2.csv")
    return nx.from_pandas_edgelist(df, 'from', 'to')


def plot_grid_graph(G):
    plt.figure(1, figsize=(10, 10))
    nx.draw(G, with_labels=True, node_size=700, node_color='lightblue', font_weight='bold', font_size=10)
    plt.show()


# Generate and plot the grid graph
# Define the dimensions of the grid
# n = 6  # number of rows
# m = 8  # number of columns
# G = generate_grid_graph(n, m)


# Import the star graph
G = import_graph()


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
    deg_1_nodes = [node for node, degree in G.degree() if degree == 1]
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
            merge(G, part)
        deg_1_nodes = [n for n in deg_1_nodes if n not in chain]


def grid_reduce(G, k=4):
    G_ = G.copy()
    while G_.number_of_nodes() > 0:
        v = list(G_.nodes)[0]
        cycle = find_cycle(G_, v, set([v]), [v], k)
        if cycle is not None:
            merge(G, cycle)
            G_.remove_nodes_from(cycle[1:])
        G_.remove_node(v)


num_reductions = 4
plot_grid_graph(G)

for i in range(num_reductions):
    chain_reduce(G)
    plot_grid_graph(G)
