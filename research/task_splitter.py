from huggingface_hub import InferenceClient
from pydantic import BaseModel
from typing import List
from config import task_planner_model_id, task_planner_provider
from .prompts import TASK_SPLITTER_SYSTEM_PROMPT

import os
import json


class Subtask(BaseModel):
    id: str
    title: str
    description: str


class SubtaskList(BaseModel):
    subtasks: List[Subtask]


TASK_SPLITTER_JSON_SCHEMA = {
    "name": "subtasklist",
    "schema": SubtaskList.model_json_schema(),
    "strict": True,
}


def split_task_into_subtasks(research_plan: str) -> List[Subtask]:
    print("Splitting the research plan into subtasks ...")
    print(f"Using Model : {task_planner_model_id}")
    print(f"Model Provider: {task_planner_provider}")

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
        },  # type: ignore
    )  # type: ignore

    message = completion.choices[0].message

    subtasks = json.loads(message.content)["subtasks"]

    print("\033[93mGenerated The Following Subtasks\033[0m")
    for task in subtasks:
        print(f"\033[93m{task['title']}\033[0m")
        print(f"\033[93m{task['description']}\033[0m")
        print()
    return subtasks
