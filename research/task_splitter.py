from huggingface_hub import InferenceClient
from pydantic import BaseModel
from .config import task_planner_model_id, task_planner_provider
from .prompts import TASK_SPLITTER_SYSTEM_PROMPT

import os
import json


class Subtask(BaseModel):
    id: str
    title: str
    description: str


class SubtaskList(BaseModel):
    subtasks: list[Subtask]


TASK_SPLITTER_JSON_SCHEMA = {
    "name": "subtasklist",
    "schema": SubtaskList.model_json_schema(),
    "strict": True,
}


def split_task_into_subtasks(research_plan: str) -> list[dict]:
    client = InferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to="huggingface",
        provider=task_planner_provider,
    )

    completion = client.chat.completions.create(
        model=task_planner_model_id,
        messages=[
            {"role": "system", "content": TASK_SPLITTER_SYSTEM_PROMPT},
            {"role": "user", "content": research_plan},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": TASK_SPLITTER_JSON_SCHEMA,
        },
    )

    subtasks = json.loads(completion.choices[0].message.content)["subtasks"]
    return subtasks
