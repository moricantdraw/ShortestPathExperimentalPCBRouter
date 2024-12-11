import networkx as nx


def is_planar_and_thickness(adj_matrix):
    """
    Determine if a graph is planar and calculate its thickness if not planar.

    Parameters:
        adj_matrix (list of list of int): The adjacency matrix of the graph.

    Returns:
        tuple: A tuple (is_planar, thickness, subgraphs) where:
               - is_planar (bool): True if the graph is planar, otherwise False.
               - thickness (int): If the graph is not planar, the thickness of the graph. If planar, 1.
               - subgraphs (list of edges): list of edges on each layer for this partition
    """
    # Convert adjacency matrix to a NetworkX graph
    G = nx.Graph()
    for i in range(len(adj_matrix)):
        for j in range(i + 1, len(adj_matrix)):
            if adj_matrix[i][j]:
                G.add_edge(i, j)

    # If not planar, calculate thickness
    # Start with an upper bound equal to the number of edges (trivial case: each edge is its own subgraph)
    edges = list(G.edges)
    n = len(edges)

    # Check if the graph is planar
    is_planar, _ = nx.check_planarity(G)

    if is_planar:
        return True, 1, edges  # A planar graph has thickness 1

    for k in range(2, n + 1):  # Check from 2 subgraphs up to the number of edges
        for decomposition in generate_partitions(edges, k):
            # Create k subgraphs
            subgraphs = [nx.Graph() for _ in range(k)]
            for i, part in enumerate(decomposition):
                subgraphs[i].add_edges_from(part)

            # Check if all subgraphs are planar
            if all(nx.check_planarity(subgraph)[0] for subgraph in subgraphs):
                return False, k, subgraphs

    return False, n, edges  # In worst case, the thickness equals the number of edges


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
