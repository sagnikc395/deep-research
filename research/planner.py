from huggingface_hub import InferenceClient

from .config import model_id, model_provider
from .prompts import PLANNER_SYSTEM_PROMPT
import os


def generate_research_plan(query: str) -> str:
    planner_client = InferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to="huggingface",
        provider=model_provider,
    )

    response = planner_client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    return response.choices[0].message.content
