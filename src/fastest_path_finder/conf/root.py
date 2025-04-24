from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class RootSettings(BaseSettings):

    animation_interval: int = 300
    map_center_point: tuple[float, float]
    map_distance: int
    network_type: str = "drive"
    start_coords: tuple[float, float]
    end_coords: tuple[float, float]
    network_type: str = "drive"
    weight: str = "travel_time"
    visited_route_color: str = "blue"
    current_route_color: str = "red"


def load_settings_from_yaml(path: str) -> dict:
    """Loads settings from a YAML file."""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Warning: YAML config file '{path}' not found. Using defaults/env vars.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{path}': {e}")
        return {}


yaml_config_data = load_settings_from_yaml("src/fastest_path_finder/config.yaml")

root_settings = RootSettings(**yaml_config_data)
