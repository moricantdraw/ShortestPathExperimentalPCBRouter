import maxflow

# Original connectivity map
connectivity_map = {
    'R1': ['C1', 'VCC', 'C2'],
    'C1': ['R1', 'GND'],
    'GND': ['C1', 'C2'],
    'VCC': ['R1'],
    'C2': ['R1', 'R2', 'GND'],
    'R2': ['C2']
}

capacity_map = {node: {neighbor: 1 for neighbor in neighbors} 
                for node, neighbors in connectivity_map.items()}

# Map nodes to unique indices
node_indices = {node: idx for idx, node in enumerate(capacity_map)}

# Create the maxflow graph and add nodes
graph = maxflow.Graph[float]()
graph.add_nodes(len(node_indices))

# Add edges
for source, neighbors in capacity_map.items():
    for target, capacity in neighbors.items():
        u = node_indices[source]
        v = node_indices[target]
        graph.add_edge(u, v, capacity, capacity)

# Define source and sink nodes
source = node_indices['VCC']
sink = node_indices['GND']

# Add terminal edges
graph.add_tedge(source, float('inf'), 0)
graph.add_tedge(sink, 0, float('inf'))

# Calculate maxflow
max_flow_value = graph.maxflow()
print("MaxFlow from VCC to GND:", max_flow_value)
