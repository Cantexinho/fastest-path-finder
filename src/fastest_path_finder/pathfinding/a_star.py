import osmnx as ox
import networkx as nx
import heapq
from typing import Tuple, List, Set, Generator


class AStar:
    """A* pathfinding algorithm implementation"""

    def __init__(self, graph: nx.MultiDiGraph, weight: str = "travel_time"):
        """
        Initialize the A* algorithm

        Args:
            graph: NetworkX graph to search
            weight: Edge attribute to use as the weight (default: travel_time)
        """
        self.graph = graph
        self.weight = weight

    @staticmethod
    def heuristic(u: int, v: int, graph: nx.MultiDiGraph) -> float:
        """Calculate the heuristic distance between two nodes"""
        x1, y1 = graph.nodes[u]["x"], graph.nodes[u]["y"]
        x2, y2 = graph.nodes[v]["x"], graph.nodes[v]["y"]
        return ox.distance.great_circle(y1, x1, y2, x2)

    def search_generator(
        self, start_node: int, end_node: int
    ) -> Generator[Tuple[int, Set[int], List[int]], None, None]:
        """
        Generator version of A* search algorithm that yields intermediate states

        Args:
            start_node: Starting node ID
            end_node: Target node ID

        Yields:
            Tuple containing (current_node, visited_nodes_set, current_path_nodes)
        """
        open_set = [(0, start_node)]
        came_from = {}
        g_score = {node: float("inf") for node in self.graph.nodes()}
        f_score = {node: float("inf") for node in self.graph.nodes()}
        g_score[start_node] = 0
        f_score[start_node] = self.heuristic(start_node, end_node, self.graph)
        visited_nodes_set = set()

        while open_set:
            current_f, current_node = heapq.heappop(open_set)
            if current_node in visited_nodes_set:
                continue

            visited_nodes_set.add(current_node)

            # Reconstruct current path
            current_path_nodes = []
            temp_curr = current_node
            while temp_curr in came_from:
                current_path_nodes.append(temp_curr)
                temp_curr = came_from[temp_curr]
            current_path_nodes.append(start_node)
            current_path_nodes.reverse()

            # Yield current state
            yield (current_node, set(visited_nodes_set), list(current_path_nodes))

            if current_node == end_node:
                print("Goal reached by generator!")
                return

            for neighbor in self.graph.successors(current_node):
                if neighbor in visited_nodes_set:
                    continue

                edge_data = self.graph.get_edge_data(current_node, neighbor)
                min_weight = min(
                    data.get(self.weight, float("inf")) for data in edge_data.values()
                )

                if min_weight == float("inf"):
                    continue

                tentative_g_score = g_score[current_node] + min_weight

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(
                        neighbor, end_node, self.graph
                    )
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        print("Path not found by generator.")
        yield (None, visited_nodes_set, [])  # Indicate failure
