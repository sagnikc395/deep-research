from huggingface_hub import InferenceClient

from .config import model_id, model_provider
from .memory import recall_relevant
from .prompts import PLANNER_SYSTEM_PROMPT
import os


def _build_memory_context(query: str) -> str:
    """Build a context block from past research sessions relevant to this query."""
    past = recall_relevant(query, limit=3)
    if not past:
        return ""

    parts = [
        "The following past research sessions may provide useful context:\n"
    ]
    for i, session in enumerate(past, 1):
        parts.append(
            f"### Past Session {i} (from {session['created_at'][:10]})\n"
            f"**Query:** {session['query']}\n"
            f"**Plan excerpt:** {session['plan'][:500]}...\n"
        )
    return "\n".join(parts)


def generate_research_plan(query: str) -> str:
    planner_client = InferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to="huggingface",
        provider=model_provider,
    )

    memory_context = _build_memory_context(query)
    user_message = query
    if memory_context:
        user_message = (
            f"{memory_context}\n---\nNew research query:\n{query}"
        )

    response = planner_client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content
