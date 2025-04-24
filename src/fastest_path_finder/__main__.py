import osmnx as ox
import networkx as nx
import heapq
import matplotlib.pyplot as plt
import time
import contextily as cx
import matplotlib.animation as animation
from collections import deque


# --- Heuristic function (remains the same) ---
def heuristic(u, v, graph):
    # ... (same as before) ...
    x1, y1 = graph.nodes[u]["x"], graph.nodes[u]["y"]
    x2, y2 = graph.nodes[v]["x"], graph.nodes[v]["y"]
    return ox.distance.great_circle(y1, x1, y2, x2)


# --- a_star_search_generator (remains the same) ---
def a_star_search_generator(graph, start_node, end_node, weight="travel_time"):
    # ... (same as before, yielding state) ...
    open_set = [(0, start_node)]
    came_from = {}
    g_score = {node: float("inf") for node in graph.nodes()}
    f_score = {node: float("inf") for node in graph.nodes()}
    g_score[start_node] = 0
    f_score[start_node] = heuristic(start_node, end_node, graph)
    visited_nodes_set = set()

    while open_set:
        current_f, current_node = heapq.heappop(open_set)
        if current_node in visited_nodes_set:
            continue
        visited_nodes_set.add(current_node)
        temp_path = []
        temp_curr = current_node
        while temp_curr in came_from:
            temp_path.append(temp_curr)
            temp_curr = came_from[temp_curr]
        temp_path.append(start_node)
        current_path_nodes = temp_path[::-1]
        yield (
            current_node,
            set(visited_nodes_set),
            list(current_path_nodes),
        )  # Yield a copy
        if current_node == end_node:
            print("Goal reached by generator!")
            return
        for neighbor in graph.successors(current_node):
            if neighbor in visited_nodes_set:
                continue
            edge_data = graph.get_edge_data(current_node, neighbor)
            min_weight = min(
                data.get(weight, float("inf")) for data in edge_data.values()
            )
            if min_weight == float("inf"):
                continue
            tentative_g_score = g_score[current_node] + min_weight
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(
                    neighbor, end_node, graph
                )
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    print("Path not found by generator.")
    yield (None, visited_nodes_set, [])  # Indicate failure


def main():
    # --- Steps 1, 2, 3: Config, Fetching, Points (Same as before) ---
    point = (54.67000, 25.26060)
    dist = 1300
    network_type = "walk"
    print(f"Fetching map data for area around {point}...")
    start_time = time.time()
    graph = ox.graph_from_point(
        point, dist=dist, network_type=network_type, simplify=True
    )
    print(f"Graph fetched in {time.time() - start_time:.2f} seconds.")
    print("Preprocessing graph...")
    start_time = time.time()
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)
    print(f"Graph preprocessed in {time.time() - start_time:.2f} seconds.")
    start_coords = (54.67299, 25.269059)
    end_coords = (54.668064, 25.250680)
    print(f"Finding nearest nodes...")
    start_node = ox.nearest_nodes(graph, start_coords[1], start_coords[0])
    end_node = ox.nearest_nodes(graph, end_coords[1], end_coords[0])
    print(f"Start node: {start_node}, End node: {end_node}")

    # --- Setup for Animation ---
    print("Projecting graph for plotting...")
    graph_proj = ox.project_graph(graph, to_crs="epsg:3857")

    print("Setting up base plot...")
    fig, ax = ox.plot_graph(
        graph_proj,
        node_size=0,
        edge_linewidth=0.5,
        edge_color="gray",
        show=False,
        close=False,
        bgcolor="#FFFFFF",
    )
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zoom="auto")
    ax.set_axis_off()

    # --- Create placeholder artists for animation ---
    # For visited nodes (scatter plot)
    scatter_visited = ax.scatter([], [], s=5, c="blue", alpha=0.2, zorder=3)
    # For the current path (line plot)
    # Initialize with empty data, choose color/style
    (line_path,) = ax.plot([], [], color="red", linewidth=2, alpha=0.7, zorder=4)
    # --------------------------------------------

    final_path_nodes = None  # To store the final result

    # --- Animation Update Function (Refactored) ---
    def update(frame_data):
        nonlocal final_path_nodes  # Allow modification of outer scope variable
        current_node, visited_nodes, current_path = frame_data

        artists_to_update = []  # For blitting

        if current_node is None and not final_path_nodes:  # Pathfinding failed
            print("Animation: No path found state received.")
            return artists_to_update  # Return empty list

        if current_node == end_node and not final_path_nodes:  # Goal reached first time
            final_path_nodes = list(current_path)
            print(f"Animation: Goal reached! Path length: {len(final_path_nodes)}")
            # Optionally change final path color here or wait for static plot later
            line_path.set_color("red")  # Make final path red

        # Update visited nodes plot
        if visited_nodes:
            try:
                valid_visited = [n for n in visited_nodes if n in graph_proj.nodes]
                if valid_visited:
                    coords = [
                        (graph_proj.nodes[n]["x"], graph_proj.nodes[n]["y"])
                        for n in valid_visited
                    ]
                    # Update scatter data directly (more efficient than remove/add)
                    scatter_visited.set_offsets(coords)
                    artists_to_update.append(scatter_visited)
            except Exception as e:
                print(f"Error updating visited node scatter plot: {e}")

        # Update current path plot
        if len(current_path) > 1:
            try:
                valid_path_nodes = [n for n in current_path if n in graph_proj.nodes]
                if len(valid_path_nodes) > 1:
                    path_coords = [
                        (graph_proj.nodes[n]["x"], graph_proj.nodes[n]["y"])
                        for n in valid_path_nodes
                    ]
                    path_x, path_y = zip(*path_coords)
                    # Update line data directly
                    line_path.set_data(path_x, path_y)
                    artists_to_update.append(line_path)
            except Exception as e:
                print(f"Error updating path line plot: {e}")
        elif len(current_path) <= 1:  # Clear the line if path is too short or empty
            line_path.set_data([], [])
            artists_to_update.append(line_path)

        return artists_to_update  # Return list of artists that were modified

    # --- Run A* Generator and Create Animation ---
    print("Starting animation generation...")
    astar_gen = a_star_search_generator(
        graph, start_node, end_node, weight="travel_time"
    )

    # Create the animation - try blit=True again now
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=astar_gen,
        interval=300,
        save_count=500,
        repeat=False,
        blit=True,
    )  # Try blit=True

    plt.show()  # Show the animation window

    # Optional: Plot final path statically after animation closes
    # if final_path_nodes:
    #     print("Plotting final static path...")
    #     # You might reuse fig/ax or create new ones if needed
    #     fig_final, ax_final = ox.plot_graph_route(
    #         graph_proj,
    #         final_path_nodes,
    #         route_color="r",
    #         route_linewidth=2,
    #         node_size=0,
    #         show=False,
    #         close=False,
    #         bgcolor="none",
    #     )
    #     cx.add_basemap(ax_final, source=cx.providers.OpenStreetMap.Mapnik, zoom="auto")
    #     ax_final.set_axis_off()
    #     plt.show()
    # elif final_path_nodes is None:
    #     print("Final check: No path was found.")

    # print("Implementation finished.")


if __name__ == "__main__":
    main()
