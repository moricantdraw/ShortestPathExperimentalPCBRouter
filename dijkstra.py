def dijkstra(grid, start, end):
    """
    Finds the shortest path from start to end using Dijkstra's Algorithm,
    parameters:
        grid: 2D list representing the PCB layout.
        start: Tuple (x, y) for the start point.
        end: Tuple (x, y) for the end point.
    returns a list of tuples representing the path from start to end, or None if no path exists.
    resource: 
    https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/
    """
    rows, cols = len(grid), len(grid[0])

    def is_valid(x, y):
        return 0 <= x < rows and 0 <= y < cols and grid[x][y] == 0

    #distances and predecessors
    distances = {start: 0}
    predecessors = {start: None}
    visited = set()

    # priority queue: list of tuples (distance, node)
    pq = [(0, start)]

    while pq:
        #finds the node with the smallest distance
        min_distance = float('inf')
        min_index = -1
        for i, (distance, node) in enumerate(pq):
            if distance < min_distance:
                min_distance = distance
                min_index = i

        # removes the node with the smallest distance from the list
        current_distance, current_node = pq.pop(min_index)

        # marks the node as visited
        visited.add(current_node)

        # if the end node is reached, reconstructs path
        if current_node == end:
            path = []
            while current_node:
                path.append(current_node)
                current_node = predecessors[current_node]
            return path[::-1]

        # explore neighbors: if new neighbor is less than the other neighbor (distances [neighbor], distances are updated such that this neighbor is used)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # Directions: right, left, down, up
            neighbor = (current_node[0] + dx, current_node[1] + dy)
            if is_valid(*neighbor) and neighbor not in visited:
                new_distance = current_distance + 1
                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_node
                    pq.append((new_distance, neighbor))

    return None  # No path found
