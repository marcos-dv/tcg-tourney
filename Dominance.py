import networkx as nx
import matplotlib.pyplot as plt

def save_dominance_graph(nodes, arcs, semi_arcs, img_path = 'dominance_graph.png', seed=33):
    # Define the list of arcs (edges), where each tuple represents an edge (from_node, to_node)

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes to the graph
    G.add_nodes_from(nodes)
    
    # Add arcs to the graph
    G.add_edges_from(arcs)
    G.add_edges_from(semi_arcs)

    # Create a layout for our nodes 
    layout = nx.circular_layout(G)
    #layout = nx.spring_layout(G, seed=seed)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos=layout, node_color='skyblue', node_size=1000)
    nx.draw_networkx_labels(G, pos=layout, font_color='black', font_weight='bold')

    # Draw primary arcs
    nx.draw_networkx_edges(G, pos=layout, edgelist=arcs, edge_color='black', arrows=True, arrowstyle='-|>', node_size=1000, width=3, connectionstyle='arc3,rad=0.2')

    # Draw additional arcs with a discontinuous arrow style
    nx.draw_networkx_edges(G, pos=layout, edgelist=semi_arcs, edge_color='grey', arrows=True, arrowstyle='-', style='-', node_size=1000, width=1, connectionstyle='arc3,rad=0.1')
    #nx.draw_networkx_edges(G, pos=layout, edgelist=semi_arcs, edge_color='grey', arrowstyle='-[', style='dashed', width=2)

    #nx.draw(G, pos=layout, with_labels=True, node_color='skyblue', node_size=2000, edge_color='k', font_size=10, font_color='black', font_weight='bold', width=2, arrowstyle='-|>')

    # Save the graph as a PNG file
    plt.savefig(img_path)

    # Optionally display the plot
    # plt.show()
    return img_path
