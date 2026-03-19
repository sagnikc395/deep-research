"""
reads from the deep-research-config.toml to read the differnt properties
and sets thing here
"""

import tomllib
import os

with open("../deep-research-config.toml", "rb") as f:
    config = tomllib.load(f)

# global level import from .env
FIRECRAWL_API_KEY = os.environ["FIRECRAWL_API_KEY"]
MCP_URL = f"https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp/"


## access the values
app_name = config["app"]["name"]
model_id = config["app"]["model_id"]
model_provider = config["app"]["model_provider"]
task_planner_model_id = config["app"]["task_planner_model_id"]
task_planner_provider = config["app"]["task_planner_provider"]
coordinator_model_id = config["app"]["coordinator_model_id"]
subagent_model_id = config["app"]["subagent_model_id"]
