from dijkstra import dijkstra

class PCBRouter:
    def __init__(self, grid):
        """
        Initializes the PCB router with a grid.
        :param grid: 2D list representing the PCB layout.
                     0 represents free space, 1 represents obstacles.
        """
        self.grid = grid

    def route(self, start, end, algorithm):
        """
        Routes a wire from start to end using the specified algorithm.
        :param start: Tuple (x, y) for the start point.
        :param end: Tuple (x, y) for the end point.
        :param algorithm: Function to use for routing.
        :return: List of tuples representing the path, or None if no path exists.
        """
        path = algorithm(self.grid, start, end)
        if path:
            for x, y in path:
                self.grid[x][y] = 2  # Mark the path on the grid
            return path
        else:
            print(f"No route found between {start} and {end}.")
            return None

    def multi_route(self, start_end_pairs, algorithm):
        """
        Routes multiple start-end pairs ensuring paths don't cross.
        :param start_end_pairs: List of tuples [(start1, end1), (start2, end2), ...].
        :param algorithm: Function to use for routing.
        :return: List of all routed paths.
        """
        all_paths = []
        for start, end in start_end_pairs:
            print(f"Routing from {start} to {end}...")
            path = self.route(start, end, algorithm)
            if path:
                all_paths.append((start, end, path))
                # Mark the path as obstacles to prevent crossings
                for x, y in path:
                    self.grid[x][y] = 1
            else:
                print(f"Failed to route from {start} to {end}.")
        return all_paths


# Example Usage
if __name__ == "__main__":
    # Create an empty grid
    rows, cols = 5, 5  # Default grid size
    pcb_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    router = PCBRouter(pcb_grid)
    
    # Ask user if they want to use Dijkstra
    print("Available algorithms:")
    print("1. Dijkstra's Algorithm")
    algorithm_choice = input("Choose routing algorithm (1 for Dijkstra): ").strip()
    
    if algorithm_choice == "1":
        algorithm = dijkstra
    else:
        print("Invalid choice. Defaulting to Dijkstra's Algorithm.")
        algorithm = dijkstra

    # Collect start-end pairs from the user
    print("Enter multiple start and end points as row and column indices (e.g., 0 0 4 4):")
    print("Separate each pair with a newline. Enter 'done' when finished.")
    
    start_end_pairs = []
    while True:
        user_input = input("Start and End (row1 col1 row2 col2): ").strip()
        if user_input.lower() == "done":
            break
        try:
            coords = list(map(int, user_input.split()))
            if len(coords) == 4:  # Corrected
                start, end = (coords[0], coords[1]), (coords[2], coords[3])
                start_end_pairs.append((start, end))
            else:
                print("Invalid input. Enter exactly four integers for each pair.")
        except ValueError:
            print("Invalid input. Please enter integers.")

    if start_end_pairs:
        paths = router.multi_route(start_end_pairs, algorithm)
        print("\nAll routed paths:")
        for start, end, path in paths:
            print(f"Path from {start} to {end}: {path}")
        
        print("\nUpdated PCB grid:")
        for row in pcb_grid:
            print(row)
    else:
        print("No start-end pairs entered.")
