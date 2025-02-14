import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

def draw_unordered_graph(nodes, arcs, semi_arcs, img_path = 'dominance_graph.png', seed=33):
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
    
def draw_graph_layers(nodes, arcs, semi_arcs, stats_df, img_path='dominance_graph.png', seed=33):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes to the graph with the 'subset' attribute based on their points
    for node in nodes:
        points = stats_df.loc[stats_df['Name'] == node, 'Points'].values[0]
        G.add_node(node, subset=points // 3)  # Assign the 'subset' attribute

    # Add arcs to the graph
    G.add_edges_from(arcs)
    G.add_edges_from(semi_arcs)
    
    scale = 2 # scale of the picture depends on number of players
    if len(nodes) <= 10:
        scale = 2
    elif len(nodes) <= 14:
        scale = 3
    elif len(nodes) <= 16:
        scale = 4
    elif len(nodes) <= 24:
        scale = 5
    else:
        scale = 6

    # default in matplotlib
    width, height = 6.4*(1+scale/3), 4.8*(1+scale/3)
    plt.figure(figsize=(width, height))

    # Create a layout for our nodes using multipartite_layout
    layout = nx.multipartite_layout(G, subset_key="subset", scale=scale)

    # Swap x and y coordinates to make layers horizontal (higher points at the top)
    for node, (x, y) in layout.items():
        # % mod 3 since layers are each 3 points. Divide by ten to not disturb the image too much
        vertical_shift = ((stats_df.loc[stats_df['Name'] == node, 'Points'].values[0]) % 3 - 1) / 10
        layout[node] = (y, x+vertical_shift)  # Swap x and y

    node_size_base = 2400
    node_size_max = 6000
    ratio_words = 0.30
    def node_max_string(s):
        return max(len(s) for s in s.split(' '))
    node_sizes = [min(node_size_max, int(node_size_base*max(1,node_max_string(node)*ratio_words))) for node in G.nodes()]
        
    labels = {node: (lambda s: s.replace(" ", "\n"))(node) for node in G.nodes()}
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos=layout, node_color='skyblue', node_size=node_sizes)
    nx.draw_networkx_labels(G, pos=layout, labels=labels, font_color='black', font_weight='bold', font_size=12)

    # Draw primary arcs
    nx.draw_networkx_edges(G, pos=layout, edgelist=arcs,
                            edge_color='green', arrows=True,
                            arrowstyle='-|>', node_size=node_sizes,
                            arrowsize=20,  # Increase this value for bigger arrows
                            width=2, connectionstyle='arc3,rad=0.2')

    # Draw additional arcs with a discontinuous arrow style
    nx.draw_networkx_edges(G, pos=layout, edgelist=semi_arcs, edge_color='gray', arrows=True, arrowstyle='-', style='-', node_size=node_sizes, width=1, connectionstyle='arc3,rad=0.1')

    # Save the graph as a PNG file
    plt.savefig(img_path)

    # Optionally display the plot
    # plt.show()
    return img_path
    
        
def save_dominance_graph(nodes, arcs, semi_arcs, stats_df, img_path = 'dominance_graph.png', seed=33):
    return draw_graph_layers(nodes, arcs, semi_arcs, stats_df, img_path, seed)
    return draw_unordered_graph(nodes, arcs, semi_arcs, img_path, seed)
    
