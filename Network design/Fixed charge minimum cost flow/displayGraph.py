import matplotlib.pyplot as plt  # Used to plot the instance
import networkx as nwx  # Used to define the graph


def addEdgesToGraph(G: nwx.Graph(), labels: list, adjacency: list) -> list:
    edges = []
    nrNodes = len(labels)
    for i in range(0, nrNodes):
        for j in range(0, nrNodes):
            if i != j and adjacency[i][j] == 1:
                edges.append((labels[i], labels[j]))
                G.add_edge(*(labels[i], labels[j]))


def displayGraph(labels: list, adjacency: list):
    # Create a graph object
    G = nwx.Graph()
    # Add nodes to graph corresponding to the labels
    G.add_nodes_from(labels)
    # Add edges corresponding to the adjacency matrix
    addEdgesToGraph(G, labels, adjacency)
    # Draw the graph
    nwx.draw(G,with_labels=True, font_weight='bold',edge_color = 'b',bbox=dict(facecolor="skyblue", edgecolor='black', boxstyle='round,pad=0.2'))
    # Show it using matplotlib
    plt.show()
