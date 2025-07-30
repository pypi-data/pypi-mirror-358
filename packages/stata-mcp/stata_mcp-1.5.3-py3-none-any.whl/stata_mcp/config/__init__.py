import os

import tomllib

# TODO: make the class could be use


class Config:
    # default config file path, and could not be changed
    CONFIG_FILE_PATH = os.path.expanduser("~/.stata-mcp/config.toml")

    def __init__(self):
        self.state = os.path.exists(self.CONFIG_FILE_PATH)

    def load_config(self) -> dict:
        if not self.state:
            return {}
        with open(self.CONFIG_FILE_PATH, "rb") as f:
            config = tomllib.load(f)
        return config

    def add_config(self, key: str, value: str):
        pass

    def delete_config(self, key: str):
        """ask whether to delete the config item"""

    def update_config(self, key: str, value: str):
        """ask whether to update the config item"""

    def get_config(self, key: str) -> str:
        pass
