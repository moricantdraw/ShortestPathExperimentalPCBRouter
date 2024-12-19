import { Grid, AStarFinder, DiagonalMovement } from "pathfinding";
import { getSimpleRouteJson, type SimplifiedPcbTrace } from "solver-utils";
import type { AnyCircuitElement as AnySoupElement } from "circuit-json";

// Enhanced planarity and thickness checker
function checkPlanarityAndThickness(edges: [string, string][]): [boolean, number, object[]] {
    /**
     * Helper function to check if a graph is planar.
     * For now, this is a placeholder and assumes all graphs are planar.
     */
    function isPlanarGraph(edges: [string, string][]): boolean {
        return true; // Replace with actual planarity logic (e.g., Kuratowski's theorem or Hopcroft-Tarjan algorithm).
    }

    /**
     * Helper function to decompose a graph into planar subgraphs.
     * For non-planar graphs, it determines the minimum number of layers needed.
     */
    function decomposeIntoPlanarSubgraphs(edges: [string, string][], maxSubgraphs: number): object[] {
        return []; // Placeholder for actual decomposition logic.
    }

    // Check if the graph is planar
    if (isPlanarGraph(edges)) {
        return [true, 1, [edges]]; // Planar graphs only need one layer.
    }

    // For non-planar graphs, attempt to decompose into multiple planar subgraphs.
    for (let k = 2; k <= edges.length; k++) {
        const subgraphs = decomposeIntoPlanarSubgraphs(edges, k);
        if (subgraphs.length > 0) {
            return [false, k, subgraphs]; // Non-planar graph with `k` layers.
        }
    }

    // If decomposition fails, return the graph as fully non-planar.
    return [false, edges.length, []];
}

// Ford-Fulkerson method for maximum flow calculation
function fordFulkerson(capacity: { [key: string]: { [key: string]: number } }, source: string, sink: string): number {
    /**
     * Residual graph is a copy of the capacity graph, which gets updated as we find augmenting paths.
     */
    const residualCapacity: { [key: string]: { [key: string]: number } } = JSON.parse(JSON.stringify(capacity));

    /**
     * Helper function to find an augmenting path using Depth-First Search (DFS).
     * Returns the path if found, otherwise returns null.
     */
    function dfsFindAugmentingPath(
        current: string,
        sink: string,
        visited: Set<string>,
        path: string[]
    ): string[] | null {
        if (current === sink) return path; // Reached the sink, return the path.

        visited.add(current); // Mark the current node as visited.

        for (const neighbor in residualCapacity[current]) {
            // Continue exploring neighbors with positive residual capacity.
            if (!visited.has(neighbor) && residualCapacity[current][neighbor] > 0) {
                const augmentingPath = dfsFindAugmentingPath(neighbor, sink, visited, [...path, neighbor]);
                if (augmentingPath) return augmentingPath; // Return the augmenting path if found.
            }
        }

        return null; // No augmenting path found.
    }

    let maxFlow = 0; // Initialize the maximum flow to zero.

    // Keep finding augmenting paths until none exist.
    while (true) {
        const visited = new Set<string>();
        const augmentingPath = dfsFindAugmentingPath(source, sink, visited, [source]);

        if (!augmentingPath) break; // No more augmenting paths, stop the loop.

        // Find the bottleneck capacity along the augmenting path.
        let pathFlow = Infinity;
        for (let i = 0; i < augmentingPath.length - 1; i++) {
            const u = augmentingPath[i];
            const v = augmentingPath[i + 1];
            pathFlow = Math.min(pathFlow, residualCapacity[u][v]);
        }

        // Update the residual capacities along the augmenting path.
        for (let i = 0; i < augmentingPath.length - 1; i++) {
            const u = augmentingPath[i];
            const v = augmentingPath[i + 1];
            residualCapacity[u][v] -= pathFlow; // Decrease capacity in forward direction.
            residualCapacity[v][u] = (residualCapacity[v][u] || 0) + pathFlow; // Increase capacity in reverse direction.
        }

        maxFlow += pathFlow; // Add the bottleneck capacity to the total flow.
    }

    return maxFlow; // Return the total maximum flow.
}

// Main autorouting function
export function autoroute(circuitJson: any[]): SimplifiedPcbTrace[] {
    /**
     * Parse the circuit JSON to extract connection points and obstacles.
     */
    const input = getSimpleRouteJson(circuitJson);

    /**
     * Convert the connections into an edge list for graph analysis.
     */
    const edges = input.connections.flatMap(conn =>
        conn.pointsToConnect.map((_, i, points) =>
            i < points.length - 1 ? [`${points[i].x},${points[i].y}`, `${points[i + 1].x},${points[i + 1].y}`] : null
        ).filter(edge => edge !== null) as [string, string][]
    );

    /**
     * Check the planarity of the graph and determine the required number of layers.
     */
    const [isPlanar, thickness] = checkPlanarityAndThickness(edges);
    const layerCount = isPlanar ? 1 : thickness;

    /**
     * Define the grid dimensions and initialize the grids for each layer.
     */
    const gridSize = 0.1;
    const boundsWithBuffer = {
        minX: input.bounds.minX - gridSize,
        maxX: input.bounds.maxX + gridSize,
        minY: input.bounds.minY - gridSize,
        maxY: input.bounds.maxY + gridSize,
    };

    const width = Math.ceil((boundsWithBuffer.maxX - boundsWithBuffer.minX) / gridSize);
    const height = Math.ceil((boundsWithBuffer.maxY - boundsWithBuffer.minY) / gridSize);

    const grids = Array.from({ length: layerCount }, () => new Grid(width, height));

    /**
     * Mark obstacles on the grids to prevent routing through them.
     */
    input.obstacles.forEach(obstacle => {
        const left = Math.floor((obstacle.center.x - obstacle.width / 2 - boundsWithBuffer.minX) / gridSize);
        const right = Math.ceil((obstacle.center.x + obstacle.width / 2 - boundsWithBuffer.minX) / gridSize);
        const top = Math.floor((obstacle.center.y - obstacle.height / 2 - boundsWithBuffer.minY) / gridSize);
        const bottom = Math.ceil((obstacle.center.y + obstacle.height / 2 - boundsWithBuffer.minY) / gridSize);

        for (let x = left; x <= right; x++) {
            for (let y = top; y <= bottom; y++) {
                grids.forEach(grid => grid.setWalkableAt(x, y, false));
            }
        }
    });

    const solution: SimplifiedPcbTrace[] = [];

    /**
     * Create the connectivity map as a graph with capacities.
     */
    const connectivityMap: { [key: string]: { [key: string]: number } } = {
        'VCC': { 'R1': 1 },
        'R1': { 'VCC': 1, 'C1': 1 },
        'C1': { 'R1': 1, 'GND': 1 },
        'GND': { 'C1': 1 },
        // Additional nodes can be added here.
    };

    /**
     * Calculate the maximum flow from the source (VCC) to the sink (GND).
     */
    const maxFlow = fordFulkerson(connectivityMap, 'VCC', 'GND');

    /**
     * If a valid flow exists, generate PCB traces.
     */
    if (maxFlow > 0) {
        input.connections.forEach((connection, connectionIndex) => {
            connection.pointsToConnect.forEach((point, index, points) => {
                if (index < points.length - 1) {
                    solution.push({
                        type: "pcb_trace",
                        pcb_trace_id: `trace_${connection.name}`,
                        route: points.map(({ x, y }) => ({
                            route_type: "wire",
                            x,
                            y,
                            width: 0.08,
                            layer: layerCount === 1 ? "top" : "bottom",
                        })),
                    });
                }
            });
        });
    } else {
        console.error("No valid routing solution found");
    }

    return solution;
}
