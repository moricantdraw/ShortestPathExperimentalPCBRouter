import { Grid, AStarFinder, DiagonalMovement } from "pathfinding";
import { getSimpleRouteJson, type SimplifiedPcbTrace } from "solver-utils";
import type { AnyCircuitElement as AnySoupElement } from "circuit-json";


// Helper function to determine if a graph is planar and calculate its thickness
function checkPlanarityAndThickness(edges: [string, string][]): [boolean, number, object[]] {
    function isPlanarGraph(edges: [string, string][]): boolean {
        const edgeSet = new Set(edges.map(edge => edge.join("-")));
        for (const [a, b] of edges) {
            for (const [c, d] of edges) {
                if (a !== c && a !== d && b !== c && b !== d) {
                    if (edgeSet.has([a, c].join("-")) && edgeSet.has([b, d].join("-")) && edgeSet.has([a, d].join("-")) && edgeSet.has([b, c].join("-"))) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    function decomposeIntoPlanarSubgraphs(edges: [string, string][], maxSubgraphs: number): object[] {
        const partitions = generatePartitions(edges, maxSubgraphs);
        for (const partition of partitions) {
            if (partition.every(subEdges => isPlanarGraph(subEdges))) {
                return partition.map(subEdges => createAdjacencyMap(subEdges));
            }
        }
        return [];
    }

    function createAdjacencyMap(edges: [string, string][]): object {
        const adjacencyMap: Record<string, string[]> = {};
        edges.forEach(([a, b]) => {
            if (!adjacencyMap[a]) adjacencyMap[a] = [];
            if (!adjacencyMap[b]) adjacencyMap[b] = [];
            adjacencyMap[a].push(b);
            adjacencyMap[b].push(a);
        });
        return adjacencyMap;
    }

    if (isPlanarGraph(edges)) {
        return [true, 1, [createAdjacencyMap(edges)]];
    }

    for (let k = 2; k <= edges.length; k++) {
        const subgraphs = decomposeIntoPlanarSubgraphs(edges, k);
        if (subgraphs.length > 0) {
            return [false, k, subgraphs];
        }
    }

    return [false, edges.length, []];
}

function* generatePartitions<T>(elements: T[], k: number): Generator<T[][]> {
    if (k === 1) yield [elements];
    else if (elements.length === k) yield elements.map(e => [e]);
    else {
        const [first, ...rest] = elements;
        for (const partition of generatePartitions(rest, k)) {
            for (let i = 0; i < partition.length; i++) {
                const newPartition = [...partition.slice(0, i), [first, ...partition[i]], ...partition.slice(i + 1)];
                yield newPartition;
            }
        }
        for (const partition of generatePartitions(rest, k - 1)) {
            yield [[first], ...partition];
        }
    }
}

// Main autorouting function
export function autoroute(circuitJson: any[]): SimplifiedPcbTrace[] {
    const input = getSimpleRouteJson(circuitJson);

    const edges = input.connections.flatMap(conn =>
        conn.pointsToConnect.map((_, i, points) =>
            i < points.length - 1 ? [`${points[i].x},${points[i].y}`, `${points[i + 1].x},${points[i + 1].y}`] : null
        ).filter(edge => edge !== null) as [string, string][]
    );

    const [isPlanar, thickness] = checkPlanarityAndThickness(edges);
    const layerCount = isPlanar ? 1 : thickness;

    const gridSize = 0.1;
    const boundsWithBuffer = {
        minX: input.bounds.minX,
        maxX: input.bounds.maxX,
        minY: input.bounds.minY,
        maxY: input.bounds.maxY,
    };

    const width = Math.ceil((boundsWithBuffer.maxX - boundsWithBuffer.minX) / gridSize) + 1;
    const height = Math.ceil((boundsWithBuffer.maxY - boundsWithBuffer.minY) / gridSize) + 1;

    const grids = Array.from({ length: layerCount }, () => new Grid(width, height));

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

    const finder = new AStarFinder({
        diagonalMovement: DiagonalMovement.OnlyWhenNoObstacles,
    });

    const solution: SimplifiedPcbTrace[] = [];
    input.connections.forEach((connection, layerIndex) => {
        const layer = layerIndex % layerCount;
        const grid = grids[layer].clone();

        connection.pointsToConnect.forEach((point, index, points) => {
            if (index < points.length - 1) {
                const start = points[index];
                const end = points[index + 1];

                const startX = Math.round((start.x - boundsWithBuffer.minX) / gridSize);
                const startY = Math.round((start.y - boundsWithBuffer.minY) / gridSize);
                const endX = Math.round((end.x - boundsWithBuffer.minX) / gridSize);
                const endY = Math.round((end.y - boundsWithBuffer.minY) / gridSize);

                const path = finder.findPath(startX, startY, endX, endY, grid.clone());
                if (path.length) {
                    path.forEach(([x, y]) => grid.setWalkableAt(x, y, false));
                    solution.push({
                        type: "pcb_trace",
                        pcb_trace_id: `trace_${connection.name}_${layer}`,
                        route: path.map(([x, y]) => ({
                            route_type: "wire",
                            x: x * gridSize + boundsWithBuffer.minX,
                            y: y * gridSize + boundsWithBuffer.minY,
                            width: 0.08,
                            layer: layer === 0 ? "top" : "bottom",
                        })),
                    });
                }
            }
        });
    });

    return solution;
}
