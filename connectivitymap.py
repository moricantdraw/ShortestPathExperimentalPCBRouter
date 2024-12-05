# Define circuit connections
connections = [
    ("R1", "C1"),
    ("C1", "GND"),
    ("R1", "VCC"),
    ("C2", "R1"),
    ("R2", "C2"),
    ("C2", "GND"),
]

# Create a connectivity map
def build_connectivity_map(connections):
    connectivity_map = {}
    
    for conn in connections:
        node1, node2 = conn
        
        # Add connections for node1
        if node1 not in connectivity_map:
            connectivity_map[node1] = []
        connectivity_map[node1].append(node2)
        
        # Add connections for node2 (undirected graph)
        if node2 not in connectivity_map:
            connectivity_map[node2] = []
        connectivity_map[node2].append(node1)
    
    return connectivity_map

# Build and print connectivity map
connectivity_map = build_connectivity_map(connections)
print("Connectivity Map:")
for node, neighbors in connectivity_map.items():
    print(f"{node}: {neighbors}")