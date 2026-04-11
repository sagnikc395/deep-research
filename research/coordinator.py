"""Pipeline orchestrator: plan → split → research → synthesize.

run_deep_research() is the single public entry point. It wires together
the four pipeline stages and persists the session to memory.
"""
import concurrent.futures

from agno.agent import Agent

from .config import coordinator_model_id, coordinator_provider
from .memory import save_session
from .models import hf_model
from .planner import generate_research_plan
from .prompts import SYNTHESIS_PROMPT_TEMPLATE
from .researcher import research_subtask
from .task_splitter import split_task_into_subtasks
from .telemetry import PipelineMetrics


def run_deep_research(query: str, log=print) -> str:
    metrics = PipelineMetrics()

    # ── Stage 1: plan ────────────────────────────────────────────────────
    log("Generating research plan...")
    plan = generate_research_plan(query, metrics=metrics, log=log)
    log("Research plan generated.")

    # ── Stage 2: split ───────────────────────────────────────────────────
    log("Splitting into subtasks...")
    subtasks = split_task_into_subtasks(plan, metrics=metrics, log=log)
    log(f"Generated {len(subtasks)} subtasks.")
    for t in subtasks:
        log(f"  [{t['id']}] {t['title']}")

    # ── Stage 3: research subtasks in parallel ───────────────────────────
    # Each research_subtask already runs its async MCP work in its own
    # OS thread, so spinning up one outer thread per subtask is safe and
    # gives us true fan-out with no event-loop contention.
    reports: dict[str, str] = {}
    log(f"Starting {len(subtasks)} researchers in parallel...")

    def _research_one(subtask: dict) -> tuple[str, str]:
        return subtask["id"], research_subtask(
            query, plan, subtask, log=log, metrics=metrics
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(subtasks)) as pool:
        futures = {pool.submit(_research_one, t): t for t in subtasks}
        for future in concurrent.futures.as_completed(futures):
            subtask_id, report = future.result()
            reports[subtask_id] = report

    # ── Stage 4: synthesize ──────────────────────────────────────────────
    log("Synthesizing final report...")
    sub_reports = "\n\n---\n\n".join(
        f"## {t['title']}\n\n{reports[t['id']]}" for t in subtasks
    )
    synthesis_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        user_query=query,
        research_plan=plan,
        sub_reports=sub_reports,
    )
    synthesizer = Agent(
        model=hf_model(coordinator_model_id, coordinator_provider),
        name="synthesizer",
        markdown=True,
    )
    synthesis_response = synthesizer.run(synthesis_prompt)
    metrics.record("synthesizer", synthesis_response.metrics, log)

    save_session(query, plan, subtasks, synthesis_response.content)
    log("Research complete.")
    metrics.report(log)
    return synthesis_response.content
