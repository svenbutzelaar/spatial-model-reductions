import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Create a graph object
df = pd.read_csv("case_studies/stylized_EU/inputs/transmission_lines.csv")
G = nx.from_pandas_edgelist(df, 'from', 'to')

print(G.edges())

nx.draw(G, with_labels=True)
# plt.show()

#  start simple line detection algorithm in the graph
lowest_degree_node = min(G.degree, key=lambda x: x[1])
print(lowest_degree_node)
print(type(lowest_degree_node))
if lowest_degree_node[1] == 1:
    line = [lowest_degree_node]
    edges_of_lowest_degree_node = G.edges(lowest_degree_node)
    print(edges_of_lowest_degree_node)
    print(type(edges_of_lowest_degree_node))
    next_node = list(edges_of_lowest_degree_node)[0][1]
    print(next_node)
    
    #  Make sure that this is iterative until the next node has more than 2 degrees.
else:
    print("No nodes with 1 edge, no lines possible.")

