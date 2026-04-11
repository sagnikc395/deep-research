"""Stage 1 — Research planner.

Produces a structured research map for a given user query.
Optionally prepends relevant past sessions from memory for context.
"""
from __future__ import annotations

from typing import Optional

from agno.agent import Agent

from .config import model_id, model_provider
from .memory import recall_relevant
from .models import hf_model
from .prompts import PLANNER_SYSTEM_PROMPT
from .telemetry import PipelineMetrics


def _memory_context(query: str) -> str:
    past = recall_relevant(query, limit=3)
    if not past:
        return ""
    lines = ["The following past research sessions may provide useful context:\n"]
    for i, s in enumerate(past, 1):
        lines.append(
            f"### Past Session {i} (from {s['created_at'][:10]})\n"
            f"**Query:** {s['query']}\n"
            f"**Plan excerpt:** {s['plan'][:500]}...\n"
        )
    return "\n".join(lines)


def generate_research_plan(
    query: str,
    metrics: Optional[PipelineMetrics] = None,
    log=print,
) -> str:
    """Return a research plan for *query* as plain text."""
    agent = Agent(
        model=hf_model(model_id, model_provider),
        instructions=PLANNER_SYSTEM_PROMPT,
        markdown=False,
    )
    ctx = _memory_context(query)
    message = f"{ctx}\n---\nNew research query:\n{query}" if ctx else query
    response = agent.run(message)
    if metrics is not None:
        metrics.record("planner", response.metrics, log)
    return response.content
