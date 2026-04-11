"""Stage 2 — Task splitter.

Decomposes a research plan into a list of non-overlapping subtasks
using Agno's structured-output support (Pydantic response_model).
"""
from agno.agent import Agent
from pydantic import BaseModel

from .config import task_planner_model_id, task_planner_provider
from .models import hf_model
from .prompts import TASK_SPLITTER_SYSTEM_PROMPT


class Subtask(BaseModel):
    id: str
    title: str
    description: str


class SubtaskList(BaseModel):
    subtasks: list[Subtask]


def split_task_into_subtasks(research_plan: str) -> list[dict]:
    """Return a list of subtask dicts (id, title, description)."""
    agent = Agent(
        model=hf_model(task_planner_model_id, task_planner_provider),
        instructions=TASK_SPLITTER_SYSTEM_PROMPT,
        response_model=SubtaskList,
    )
    result = agent.run(research_plan)
    return [s.model_dump() for s in result.content.subtasks]
