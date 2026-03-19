from pathlib import Path

_prompts_dir = Path(__file__).resolve().parent.parent / "prompts"

PLANNER_SYSTEM_PROMPT = (_prompts_dir / "planner_system_instructions.md").read_text()

TASK_SPLITTER_SYSTEM_PROMPT = (_prompts_dir / "task_splitter_instructions.md").read_text()

SUBAGENT_PROMPT_TEMPLATE = (_prompts_dir / "subagent_prompt.md").read_text()

COORDINATOR_PROMPT_TEMPLATE = (_prompts_dir / "coordinator_prompt.md").read_text()
