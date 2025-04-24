import matplotlib.pyplot as plt
from typing import Tuple

from src.fastest_path_finder.mapping.map_data import MapData
from src.fastest_path_finder.pathfinding.a_star import AStar
from src.fastest_path_finder.visualizing.path_visualizer import PathVisualizer


class NavigationApp:
    """Main application class integrating all components"""

    def __init__(self):
        """Initialize the application"""
        self.map_data = None
        self.astar = None
        self.visualizer = None

    def setup(
        self,
        center_point: Tuple[float, float],
        distance: int,
        network_type: str = "walk",
    ) -> None:
        """
        Set up the application components

        Args:
            center_point: Center point (lat, lng) for the map
            distance: Search radius in meters
            network_type: Type of network (walk, drive, bike, etc.)
        """
        # Set up map data
        self.map_data = MapData(center_point, distance, network_type)
        self.map_data.preprocess_graph()
        self.map_data.project_graph()

        # Set up A* algorithm
        self.astar = AStar(self.map_data.graph)

        # Set up visualizer
        self.visualizer = PathVisualizer(self.map_data.graph_proj)

    def run(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        show_animation: bool = True,
        show_final_path: bool = False,
    ) -> None:
        """
        Run the navigation application

        Args:
            start_coords: Starting coordinates (lat, lng)
            end_coords: Destination coordinates (lat, lng)
            show_animation: Whether to show the animation
            show_final_path: Whether to show the final path after animation
        """
        print(f"Finding nearest nodes...")
        start_node = self.map_data.find_nearest_node(start_coords)
        end_node = self.map_data.find_nearest_node(end_coords)
        print(f"Start node: {start_node}, End node: {end_node}")

        # Start A* search
        astar_gen = self.astar.search_generator(start_node, end_node)

        if show_animation:
            print("Starting animation generation...")
            ani = self.visualizer.animate_search(astar_gen, end_node)
            plt.show()

            # Show final path if requested
            if show_final_path and self.visualizer.final_path_nodes:
                fig_final, ax_final = self.visualizer.plot_final_path()
                if fig_final:
                    plt.figure(fig_final.number)
                    plt.show()
