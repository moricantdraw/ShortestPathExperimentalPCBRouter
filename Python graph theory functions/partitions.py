import networkx as nx
import matplotlib.pyplot as plt


def is_planar_and_thickness(edges):
    """
    Determine if a graph is planar and calculate its thickness if not planar. Return and draws the graphs that would be on each layer.

    Parameters:
        edges (list of tuples): List of tuples where the first index of the tuple is the start node and the second index is the end node

    Returns:
        tuple: A tuple (is_planar, thickness, subgraphs) where:
               - is_planar (bool): True if the graph is planar, otherwise False
               - thickness (int): If the graph is not planar, the thickness of the graph. If planar, 1
               - connectivity_map_list (list of connectivity maps): list of connectivity maps for each layer
    """
    # Convert list of edges to a networkx graph
    G = nx.Graph()
    G.add_edges_from(edges)

    # If not planar, calculate thickness
    # Start with an upper bound equal to the number of edges (trivial case: each edge is its own subgraph)
    edges = list(G.edges)
    print(edges)
    n = len(edges)

    # Check if the graph is planar
    is_planar, _ = nx.check_planarity(G)

    if is_planar:
        connectivity_map = {node: list(neighbors) for node, neighbors in G.adjacency()}
        return True, 1, [connectivity_map]  # A planar graph has thickness 1

    for k in range(2, n + 1):  # Check from 2 subgraphs up to the number of edges
        for decomposition in generate_partitions(edges, k):
            # Create k subgraphs
            subgraphs = [nx.Graph() for _ in range(k)]
            for i, part in enumerate(decomposition):
                subgraphs[i].add_edges_from(part)

            # Check if all subgraphs are planar
            if all(nx.check_planarity(subgraph)[0] for subgraph in subgraphs):
                connectivity_map_list = []
                for subgraph in subgraphs:
                    connectivity_map = {
                        node: list(neighbors)
                        for node, neighbors in subgraph.adjacency()
                    }
                    connectivity_map_list.append(connectivity_map)
                    plt.figure()
                    nx.draw(subgraph)
                return False, k, connectivity_map_list

    # In worst case, the thickness equals the number of edges
    connectivity_map_list = []
    for i in range(len(edges)):
        connectivity_map = {edges[0]: edges[1]}
        connectivity_map_list.append(connectivity_map)
    return False, n, connectivity_map_list


def generate_partitions(elements, k):
    """
    Generate all ways to partition a list of elements into k subsets.

    Parameters:
        elements (list): The elements to partition.
        k (int): The number of subsets.

    Returns:
        generator: Yields partitions as a list of k subsets.
    """
    if k == 1:
        # Base case: Only one subset, which contains all elements.
        yield [elements]
        return

    if len(elements) == k:
        # Base case: Each element must be in its own subset.
        yield [[e] for e in elements]
        return

    first, rest = elements[0], elements[1:]

    # Case 1: Place the first element in an existing subset
    for partition in generate_partitions(rest, k):
        for i in range(len(partition)):
            new_partition = (
                partition[:i] + [[first] + partition[i]] + partition[i + 1 :]
            )
            yield new_partition

    # Case 2: Place the first element in a new subset
    for partition in generate_partitions(rest, k - 1):
        yield [[first]] + partition
