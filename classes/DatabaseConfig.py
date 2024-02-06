import json
import os
class DatabaseConfig:
    def __init__(self):
        config_file_path = 'database_config.json'
        self.config = self.load_config(config_file_path)
        self.get_values()

    def load_config(self, config_file_path):
        try:
            with open(config_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception("Config file not found.")

    def get_values(self):
        self.hostname = self.config.get("hostname")
        self.database = self.config.get("database")
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.scheme = self.config.get("schema_name")
        self.connection_string = f"postgresql://{self.username}:{self.password}@{self.hostname}/{self.database}"
