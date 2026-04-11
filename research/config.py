import tomllib
import os
from pathlib import Path

_config_path = Path(__file__).resolve().parent.parent / "deep-research-config.toml"

with open(_config_path, "rb") as f:
    _cfg = tomllib.load(f)["app"]

FIRECRAWL_API_KEY = os.environ["FIRECRAWL_API_KEY"]
MCP_URL = f"https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp/"

model_id                 = _cfg["model_id"]
model_provider           = _cfg["model_provider"]
task_planner_model_id    = _cfg["task_planner_model_id"]
task_planner_provider    = _cfg["task_planner_provider"]
coordinator_model_id     = _cfg["coordinator_model_id"]
coordinator_provider     = _cfg.get("coordinator_provider", "novita")
subagent_model_id        = _cfg["subagent_model_id"]
subagent_provider        = _cfg.get("subagent_provider", "novita")
