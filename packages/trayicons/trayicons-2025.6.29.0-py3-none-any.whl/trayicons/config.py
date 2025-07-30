import argparse
import os
import toml
from pathlib import Path


class IconConfig:
    """
    Represents a single icon configuration.
    """

    def __init__(self, src, dst, toml_file_path):
        """
        Initializes an IconConfig object.

        Args:
            src (str): The source file path.
            dst (str): The destination file path.
        """
        p = Path(toml_file_path).resolve().parent
        self.src = p.joinpath(src).resolve()
        if not self.src.exists():
            print(f"config error: path {self.src} not exists.")
            exit(-1)
        self.dst = p.joinpath(dst).resolve()

    def __repr__(self):
        """
        Returns a string representation of the IconConfig object.
        """
        return f"IconConfig(src='{self.src}', dst='{self.dst}')"


class Config:
    """
    Represents the overall application configuration, including a list of icon configurations.
    """

    def __init__(self):
        """
        Initializes a Config object.
        """
        self.icons: list[IconConfig] = []  # List to store IconConfig objects

    def add_icon_config(self, icon_config):
        """
        Adds an IconConfig object to the configuration.

        Args:
            icon_config (IconConfig): The IconConfig object to add.
        """
        self.icons.append(icon_config)

    @staticmethod
    def _parse_icon_data(icon_data, toml_file_path):
        """
        Parses a single icon data entry from the TOML file.
        """
        try:
            return IconConfig(icon_data["src"], icon_data["dst"], toml_file_path)
        except KeyError as e:
            print(f"Warning: Incomplete icon configuration: Missing key {e} in {icon_data}")
            return None  # Or raise an exception, depending on desired behavior


    @classmethod
    def from_toml(cls, toml_file_path: str):
        """Loads config from TOML, handling 'icon' or 'icons' and converting 'icon' to 'icons'."""
        try:
            toml_data = toml.loads(Path(toml_file_path).read_text(encoding="utf8"))
        except toml.TomlDecodeError as e:
            raise ValueError(f"Error decoding TOML: {e}")  # Re-raise for better error handling

        # Convert 'icon' to 'icons' if necessary
        if "icon" in toml_data:
            toml_data["icons"] = toml_data.pop("icon")  # Use pop for atomicity and to remove 'icon'
            Path(toml_file_path).write_text(toml.dumps(toml_data), encoding="utf8")
            print("Note: Converted 'icon' config to 'icons' format.")

        # Main parsing logic
        if "icons" not in toml_data:
            raise ValueError(f"No 'icons' table found in TOML file: {toml_file_path}")

        config = cls()
        config.icons = [
            icon_config
            for icon_data in toml_data["icons"]
            if (icon_config := cls._parse_icon_data(icon_data, toml_file_path)) is not None
        ]
        if not config.icons:
            raise ValueError(f"No valid icon configurations found in: {toml_file_path}")

        return config

    def __iter__(self):  # Keep these for compatibility
        return iter(self.icons)

    def __len__(self):
        return len(self.icons)


# --- Utility function (unchanged, but included for completeness) ---
def get_config_path() -> Path:
    parser = argparse.ArgumentParser(
        description="A program that loads configuration files."
    )

    # Optional argument for specifying the config file
    parser.add_argument(
        "--config",
        "-c",  # Short option
        type=str,
        help="Path to the configuration file.",
        metavar="FILE",
    )

    # Positional argument for the config file (optional)
    parser.add_argument(
        "config_file",
        nargs="?",  # Allows 0 or 1 positional arguments
        type=str,
        help="Optional path to the configuration file (can also use --config).",
        metavar="FILE",
    )

    args = parser.parse_args()

    cr = Path(os.getcwd()).resolve()

    config_path = None

    if args.config:
        config_path = cr.joinpath(args.config)
    elif args.config_file:
        config_path = cr.joinpath(args.config_file)

    if config_path is None:
        config_path = cr.joinpath("icons.toml")
        if not config_path.exists():
            print(f"Default config '{config_path}' not found.")
            print("creating...")
            Path(config_path).write_text(
                encoding="utf8",
                data="""
[[icons]]
src = "demo.kra"
dst = "./demo.ico"
""",
            )
            print("please correct the config then run the tool again.")
            exit(-1)

    return config_path
