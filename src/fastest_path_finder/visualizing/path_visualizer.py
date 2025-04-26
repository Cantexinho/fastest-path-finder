import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import contextily as cx
import matplotlib.animation as animation
from typing import Generator, Any
from src.fastest_path_finder.conf.root import root_settings


class PathVisualizer:
    """Visualization class for pathfinding process"""

    def __init__(self, graph_proj: nx.MultiDiGraph):
        """
        Initialize the visualizer

        Args:
            graph_proj: Projected graph for visualization
        """
        self.graph_proj = graph_proj
        self.fig = None
        self.ax = None
        self.scatter_visited = None
        self.line_path = None
        self.final_path_nodes = None

    def setup_plot(self) -> tuple[plt.Figure, plt.Axes]:
        """Set up the plot for visualization"""
        print("Setting up base plot...")
        self.fig, self.ax = ox.plot_graph(
            self.graph_proj,
            node_size=0,
            edge_linewidth=0.5,
            edge_color="gray",
            show=False,
            close=False,
            bgcolor="#FFFFFF",
        )
        print("Adding basemap...")
        cx.add_basemap(self.ax, source=cx.providers.OpenStreetMap.Mapnik, zoom="auto")
        self.ax.set_axis_off()

        print("Creating placeholder artists for animation")
        self.scatter_visited = self.ax.scatter(
            [], [], s=5, c=root_settings.visited_route_color, alpha=0.2, zorder=3
        )
        (self.line_path,) = self.ax.plot(
            [],
            [],
            color=root_settings.current_route_color,
            linewidth=2,
            alpha=0.7,
            zorder=4,
        )

        return self.fig, self.ax

    def update_frame(self, frame_data: tuple[int, set[int], list[int]]) -> list[Any]:
        """
        Update function for animation frames

        Args:
            frame_data: tuple of (current_node, visited_nodes, current_path)

        Returns:
            List of artists that were modified
        """
        current_node, visited_nodes, current_path = frame_data
        artists_to_update = []

        if current_node is None and not self.final_path_nodes:
            print("Animation: No path found state received.")
            return artists_to_update

        if current_node == self.end_node and not self.final_path_nodes:
            self.final_path_nodes = list(current_path)
            print(f"Animation: Goal reached! Path length: {len(self.final_path_nodes)}")
            self.line_path.set_color(root_settings.current_route_color)

        if visited_nodes:
            try:
                valid_visited = [n for n in visited_nodes if n in self.graph_proj.nodes]
                if valid_visited:
                    coords = [
                        (self.graph_proj.nodes[n]["x"], self.graph_proj.nodes[n]["y"])
                        for n in valid_visited
                    ]
                    print(f"Animation: Updating visited nodes: {len(coords)}")
                    self.scatter_visited.set_offsets(coords)
                    artists_to_update.append(self.scatter_visited)
            except Exception as e:
                print(f"Error updating visited node scatter plot: {e}")

        if len(current_path) > 1:
            try:
                valid_path_nodes = [
                    n for n in current_path if n in self.graph_proj.nodes
                ]
                if len(valid_path_nodes) > 1:
                    path_coords = [
                        (self.graph_proj.nodes[n]["x"], self.graph_proj.nodes[n]["y"])
                        for n in valid_path_nodes
                    ]
                    path_x, path_y = zip(*path_coords)
                    self.line_path.set_data(path_x, path_y)
                    artists_to_update.append(self.line_path)
            except Exception as e:
                print(f"Error updating path line plot: {e}")
        elif len(current_path) <= 1:
            self.line_path.set_data([], [])
            artists_to_update.append(self.line_path)
        print("Rendering frame...")
        return artists_to_update

    def animate_search(
        self, astar_generator: Generator, end_node: int, interval: int = 300
    ) -> animation.FuncAnimation:
        """
        Create and run the animation

        Args:
            astar_generator: Generator producing search states
            end_node: Target node ID
            interval: Time between frames in milliseconds

        Returns:
            The animation object
        """
        self.end_node = end_node

        if self.fig is None or self.ax is None:
            self.setup_plot()

        print("Creating animation...")
        ani = animation.FuncAnimation(
            self.fig,
            self.update_frame,
            frames=astar_generator,
            interval=interval,
            save_count=500,
            repeat=False,
            blit=False,
        )

        return ani

    def plot_final_path(self) -> tuple[plt.Figure, plt.Axes] | None:
        """Plot the final path statically after animation"""
        if not self.final_path_nodes:
            print("No final path to display")
            return None

        print("Plotting final static path...")
        fig_final, ax_final = ox.plot_graph_route(
            self.graph_proj,
            self.final_path_nodes,
            route_color=root_settings.current_route_color,
            route_linewidth=2,
            node_size=0,
            show=False,
            close=False,
            bgcolor="none",
        )

        cx.add_basemap(ax_final, source=cx.providers.OpenStreetMap.Mapnik, zoom="auto")
        ax_final.set_axis_off()

        return fig_final, ax_final
