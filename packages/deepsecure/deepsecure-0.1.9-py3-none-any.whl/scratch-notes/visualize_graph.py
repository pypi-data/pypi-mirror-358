import json
import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(json_path="mem.json"):
    """Reads the JSON graph data and visualizes it."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_path}")
        return

    G = nx.DiGraph() # Use DiGraph for directed edges

    # Add nodes
    node_labels = {}
    for node_data in data.get("nodes", []):
        node_name = node_data.get("name")
        if node_name:
            G.add_node(node_name)
            # Keep labels simple for basic visualization
            node_labels[node_name] = node_name

    # Add edges
    edge_labels = {}
    for edge_data in data.get("edges", []):
        source = edge_data.get("source")
        target = edge_data.get("target")
        name = edge_data.get("name", "") # Use edge name as label
        description = edge_data.get("description", "")

        if source in G and target in G:
            G.add_edge(source, target)
            # Combine name and potentially description for edge label if needed
            edge_labels[(source, target)] = f"{name}"
            # If you want the full description on the edge (can get crowded):
            # edge_labels[(source, target)] = f"{name}: {description}"

    # --- Visualization ---
    plt.figure(figsize=(18, 18)) # Adjust figure size as needed

    # Choose a layout algorithm (experiment for best results)
    # pos = nx.spring_layout(G, k=0.5, iterations=50)
    # pos = nx.kamada_kawai_layout(G)
    # pos = nx.spectral_layout(G)
    pos = nx.circular_layout(G) # Often simpler for overview
    # pos = nx.shell_layout(G) # Group nodes

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='skyblue', alpha=0.9)

    # Draw edges
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, edge_color='gray', alpha=0.7)

    # Draw node labels
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)

    # Draw edge labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color='red')

    plt.title("DeepSecure CLI Structure Graph", size=20)
    plt.axis('off') # Turn off axis
    plt.tight_layout()
    plt.savefig("graph_visualization.png") # Save the graph to a file
    print("Graph visualization saved to graph_visualization.png")
    # Or display it directly:
    # plt.show()

if __name__ == "__main__":
    visualize_graph()
