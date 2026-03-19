from pathlib import Path

from huggingface_hub import InferenceClient

from config import model_id, model_provider
import os


PLANNER_SYSTEM_PROMPT = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "planner_system_instructions.md"
).read_text()


def generate_research_plan(query):
    planner_client = InferenceClient(
        api_key=os.environ["HF_TOKEN"], bill_to="huggingface", provider=model_provider
    )

    return planner_client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        stream=True,
    )
