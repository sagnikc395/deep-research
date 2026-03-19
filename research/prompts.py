from pathlib import Path

# utility to read all the prompts to read
# add here youir custom prompt reader


TASK_SPLITTER_SYSTEM_PROMPT = (
    Path(__file__).resolve().parent.parent / "prompts" / "task_splitter_instructions.md"
).read_text()

PLANNER_SYSTEM_PROMPT = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "planner_system_instructions.md"
).read_text()
