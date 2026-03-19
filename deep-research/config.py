"""
reads from the deep-research-config.toml to read the differnt properties
and sets thing here
"""

import tomllib

with open("../deep-research-config.toml", "rb") as f:
    config = tomllib.load(f)

## access the values
app_name = config["app"]["name"]
input_path = config["files"]["input_path"]
db_port = config["database"]["port"]

"""
writing to the toml file 
import tomli_w

config = {
    "app": {"name": "MyApp", "debug": True},
    "files": {
        "input_path": "data/input.csv",
        "output_path": "data/output.csv",
    }
}

with open("config.toml", "wb") as f:  # must be "wb"
    tomli_w.dump(config, f)
"""
