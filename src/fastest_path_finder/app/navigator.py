import matplotlib.pyplot as plt

from src.fastest_path_finder.mapping.map_data import MapData
from src.fastest_path_finder.pathfinding.a_star import AStar
from src.fastest_path_finder.visualizing.path_visualizer import PathVisualizer
from src.fastest_path_finder.conf.root import root_settings


class NavigationApp:
    """Main application class integrating all components"""

    def __init__(self):
        """Initialize the application"""
        self.map_data = None
        self.astar = None
        self.visualizer = None

    def setup(
        self,
        center_point: tuple[float, float],
        distance: int,
        network_type: str = "walk",
        weight: str = "travel_time",
    ) -> None:
        """
        Set up the application components

        Args:
            center_point: Center point (lat, lng) for the map
            distance: Search radius in meters
            network_type: Type of network (walk, drive, bike, etc.)
        """
        self.map_data = MapData(center_point, distance, network_type)
        self.map_data.preprocess_graph()
        self.map_data.project_graph()

        self.astar = AStar(self.map_data.graph, weight)
        self.visualizer = PathVisualizer(self.map_data.graph_proj)

    def run(
        self,
        start_coords: tuple[float, float],
        end_coords: tuple[float, float],
    ) -> None:
        """
        Run the navigation application

        Args:
            start_coords: Starting coordinates (lat, lng)
            end_coords: Destination coordinates (lat, lng)
        """
        print(f"Finding nearest nodes...")
        start_node = self.map_data.find_nearest_node(start_coords)
        end_node = self.map_data.find_nearest_node(end_coords)
        print(f"Start node: {start_node}, End node: {end_node}")

        astar_gen = self.astar.search_generator(start_node, end_node)

        print(f"Starting animation generation...")
        ani = self.visualizer.animate_search(
            astar_gen, end_node, root_settings.animation_interval
        )
        plt.show()
