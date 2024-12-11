from dataclasses import dataclass
from typing import List, Dict, Literal, Union, Optional
import heapq
from typing import Tuple, Optional

circuit_json1 = [
    {"type": "rect", "center": {"x": 5, "y": 5}, "width": 2, "height": 3},
    {"type": "rect", "center": {"x": 15, "y": 10}, "width": 4, "height": 2},
    {"name": "trace1", "pointsToConnect": [{"x": 1, "y": 1}, {"x": 20, "y": 15}]},
]

circuit_json2 = [
    {"type": "rect", "center": {"x": 8, "y": 8}, "width": 3, "height": 3},
    {"type": "rect", "center": {"x": 18, "y": 12}, "width": 2, "height": 5},
    {"type": "rect", "center": {"x": 25, "y": 25}, "width": 6, "height": 2},
    {"name": "trace2", "pointsToConnect": [{"x": 0, "y": 0}, {"x": 30, "y": 30}]},
    {"name": "trace3", "pointsToConnect": [{"x": 5, "y": 10}, {"x": 20, "y": 20}]},
]

circuit_json3 = [
    {"type": "rect", "center": {"x": 5, "y": 5}, "width": 3, "height": 2},
    {"center": {"x": 15, "y": 10}, "width": 4, "height": 4},  # Missing "type"
    {"name": "trace4", "pointsToConnect": [{"x": 2, "y": 2}, {"x": 25, "y": 25}]},
]

circuit_json4 = [
    {"type": "rect", "center": {"x": 10, "y": 10}, "width": 5, "height": 3},
    {"type": "rect", "center": {"x": 20, "y": 20}, "width": 3, "height": 3},
    {
        "name": "trace5",
        "pointsToConnect": [
            {"x": 0, "y": 0},
            {"x": 15, "y": 15},
            {"x": 30, "y": 30},
        ],
    },
]


@dataclass
class PcbTraceRoute:
    route_type: Literal["wire"]
    x: float
    y: float
    width: float
    layer: Literal["top", "bottom"]


@dataclass
class SimplifiedPcbTrace:
    type: Literal["pcb_trace"]
    pcb_trace_id: str
    route: List[PcbTraceRoute]


@dataclass
class Obstacle:
    type: Literal["rect"]  # Note: most datasets do not contain ovals
    center: Dict[str, float]  # {"x": float, "y": float}
    width: float
    height: float
    connectedTo: List[str]


@dataclass
class Connection:
    name: str
    pointsToConnect: List[Dict[str, float]]  # [{"x": float, "y": float}]


@dataclass
class Bounds:
    minX: float
    maxX: float
    minY: float
    maxY: float


@dataclass
class SimpleRouteJson:
    layerCount: int
    obstacles: List[Obstacle]
    connections: List[Connection]
    bounds: Bounds


# Assuming get_simple_route_json is an existing function similar to getSimpleRouteJson in TypeScript
def get_simple_route_json(circuit_json: List[Dict]) -> SimpleRouteJson:
    """
    Converts circuit data into a SimpleRouteJson format.
    """
    # Placeholder parsing logic.

    # Example transformation of circuit elements into obstacles
    obstacles = [
        Obstacle(
            type="rect",
            center={"x": elem["center"]["x"], "y": elem["center"]["y"]},
            width=elem["width"],
            height=elem["height"],
            connectedTo=elem.get("connectedTo", []),
        )
        for elem in circuit_json
        if elem.get("type") == "rect"  # Safely check for the "type" key
    ]

    # Example transformation of connections
    connections = [
        Connection(
            name=conn["name"],
            pointsToConnect=[
                {"x": pt["x"], "y": pt["y"]} for pt in conn["pointsToConnect"]
            ],
        )
        for conn in circuit_json
        if "pointsToConnect" in conn
    ]

    # Calculate bounds dynamically
    all_x = [pt["x"] for conn in connections for pt in conn.pointsToConnect]
    all_y = [pt["y"] for conn in connections for pt in conn.pointsToConnect]
    min_x = min(all_x) if all_x else 0
    max_x = max(all_x) if all_x else 0
    min_y = min(all_y) if all_y else 0
    max_y = max(all_y) if all_y else 0

    # Create bounds
    bounds = Bounds(minX=min_x, maxX=max_x, minY=min_y, maxY=max_y)

    # Assuming a default layerCount of 2 (top and bottom)
    return SimpleRouteJson(
        layerCount=2, obstacles=obstacles, connections=connections, bounds=bounds
    )


# Define a helper function to calculate the Manhattan distance (heuristic)
def manhattan_distance(start: Tuple[float, float], goal: Tuple[float, float]) -> float:
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])


# Define the A* pathfinding function
def a_star(
    grid: List[List[int]], start: Tuple[int, int], goal: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """
    A* pathfinding algorithm to find the shortest path from start to goal on a 2D grid.
    `grid` is a 2D list where 0 represents a free cell, and 1 represents an obstacle.
    """
    rows, cols = len(grid), len(grid[0])
    open_set = []  # Priority queue for the A* search
    heapq.heappush(open_set, (0, start))  # (f_score, node)

    came_from = {}  # To reconstruct the path
    g_score = {start: 0}  # Cost from start to current node
    f_score = {start: manhattan_distance(start, goal)}  # Estimated cost to goal

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            # Reconstruct the path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]  # Reverse the path

        x, y = current
        for dx, dy in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]:  # Neighboring nodes (up, down, left, right)
            neighbor = (x + dx, y + dy)

            if (
                0 <= neighbor[0] < rows
                and 0 <= neighbor[1] < cols
                and grid[neighbor[0]][neighbor[1]] == 0
            ):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + manhattan_distance(
                        neighbor, goal
                    )
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found


# Updated autoroute function to use A*
def autoroute(circuit_json, num_layers):
    if num_layers < 1:
        raise ValueError("Number of layers must be at least 1.")

    # Distribute connections across layers
    connections = [elem for elem in circuit_json if "pointsToConnect" in elem]
    obstacles = [elem for elem in circuit_json if elem.get("type") == "rect"]

    # Divide connections into layers
    layer_connections = [[] for _ in range(num_layers)]
    for i, connection in enumerate(connections):
        layer_index = i % num_layers  # Round-robin allocation
        layer_connections[layer_index].append(connection)

    # Process each layer
    for layer_index in range(num_layers):
        print(f"Routing for Layer {layer_index + 1}...")
        current_layer_obstacles = [
            obs for obs in obstacles if obs.get("layer", 1) == layer_index + 1
        ]
        current_layer_connections = layer_connections[layer_index]

        # Call routing logic for this layer
        route_layer(current_layer_obstacles, current_layer_connections)

def route_layer(obstacles, connections):
    # Dummy function for routing on a single layer
    print(f"Obstacles: {obstacles}")
    print(f"Connections: {connections}")


autoroute(circuit_json2, num_layers=2)

