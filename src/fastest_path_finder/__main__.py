from src.fastest_path_finder.app.navigator import NavigationApp
from src.fastest_path_finder.conf.root import root_settings


def main():
    """Main function to run the application"""

    app = NavigationApp()
    app.setup(
        root_settings.map_center_point,
        root_settings.map_distance,
        root_settings.network_type,
        root_settings.weight,
    )
    app.run(root_settings.start_coords, root_settings.end_coords)


if __name__ == "__main__":
    main()
