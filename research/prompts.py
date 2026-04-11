from pathlib import Path

_dir = Path(__file__).resolve().parent.parent / "prompts"

PLANNER_SYSTEM_PROMPT       = (_dir / "planner_system_instructions.md").read_text()
TASK_SPLITTER_SYSTEM_PROMPT = (_dir / "task_splitter_instructions.md").read_text()
SUBAGENT_PROMPT_TEMPLATE    = (_dir / "subagent_prompt.md").read_text()
COORDINATOR_PROMPT_TEMPLATE = (_dir / "coordinator_prompt.md").read_text()
SYNTHESIS_PROMPT_TEMPLATE   = (_dir / "synthesis_prompt.md").read_text()
