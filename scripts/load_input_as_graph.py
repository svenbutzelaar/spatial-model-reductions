import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Create a graph object
df = pd.read_csv("case_studies/stylized_EU/inputs/transmission_lines.csv")
G = nx.from_pandas_edgelist(df, 'from', 'to')

print(G.edges())

nx.draw(G, with_labels=True)
plt.show()


