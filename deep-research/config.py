"""
reads from the deep-research-config.toml to read the differnt properties
and sets thing here
"""

import tomllib

with open("../deep-research-config.toml", "rb") as f:
    config = tomllib.load(f)

## access the values
app_name = config["app"]["name"]
model_id = config["app"]["model_id"]
model_provider = config["app"]["model_provider"]
