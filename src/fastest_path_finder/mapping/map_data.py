import osmnx as ox
import networkx as nx
import time


class MapData:
    """Handle map data acquisition and processing"""

    def __init__(
        self,
        center_point: tuple[float, float],
        distance: int,
        network_type: str = "walk",
    ):
        """
        Initialize and fetch map data

        Args:
            center_point: (lat, lng) coordinates
            distance: Search radius in meters
            network_type: Type of network to extract (walk, drive, bike, etc.)
        """
        self.center_point = center_point
        self.distance = distance
        self.network_type = network_type
        self.graph = None
        self.graph_proj = None

    def fetch_graph(self) -> nx.MultiDiGraph:
        """Fetch and process the graph"""
        print(f"Fetching map data for area around {self.center_point}...")
        start_time = time.time()

        self.graph = ox.graph_from_point(
            self.center_point,
            dist=self.distance,
            network_type=self.network_type,
            simplify=True,
        )

        print(f"Graph fetched in {time.time() - start_time:.2f} seconds.")
        return self.graph

    def preprocess_graph(self) -> nx.MultiDiGraph:
        """Add speed and travel time attributes to the graph"""
        if self.graph is None:
            self.fetch_graph()

        print("Preprocessing graph...")
        start_time = time.time()

        self.graph = ox.add_edge_speeds(self.graph)
        self.graph = ox.add_edge_travel_times(self.graph)

        print(f"Graph preprocessed in {time.time() - start_time:.2f} seconds.")
        return self.graph

    def project_graph(self) -> nx.MultiDiGraph:
        """Project graph to Web Mercator for visualization"""
        if self.graph is None:
            self.preprocess_graph()

        print("Projecting graph for plotting...")
        self.graph_proj = ox.project_graph(self.graph, to_crs="epsg:3857")
        return self.graph_proj

    def find_nearest_node(self, point: tuple[float, float]) -> int:
        """Find the nearest node to the given coordinates"""
        if self.graph is None:
            self.preprocess_graph()

        return ox.nearest_nodes(self.graph, point[1], point[0])
