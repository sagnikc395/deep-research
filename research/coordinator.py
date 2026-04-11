"""Pipeline orchestrator: plan → split → research → synthesize.

run_deep_research() is the single public entry point. It wires together
the four pipeline stages and persists the session to memory.
"""
from agno.agent import Agent

from .config import coordinator_model_id, coordinator_provider
from .memory import save_session
from .models import hf_model
from .planner import generate_research_plan
from .prompts import SYNTHESIS_PROMPT_TEMPLATE
from .researcher import research_subtask
from .task_splitter import split_task_into_subtasks


def run_deep_research(query: str, log=print) -> str:
    # ── Stage 1: plan ────────────────────────────────────────────────────
    log("Generating research plan...")
    plan = generate_research_plan(query)
    log("Research plan generated.")

    # ── Stage 2: split ───────────────────────────────────────────────────
    log("Splitting into subtasks...")
    subtasks = split_task_into_subtasks(plan)
    log(f"Generated {len(subtasks)} subtasks.")
    for t in subtasks:
        log(f"  [{t['id']}] {t['title']}")

    # ── Stage 3: research each subtask ───────────────────────────────────
    reports: dict[str, str] = {}
    for subtask in subtasks:
        reports[subtask["id"]] = research_subtask(query, plan, subtask, log=log)

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
    final_report = synthesizer.run(synthesis_prompt).content

    save_session(query, plan, subtasks, final_report)
    log("Research complete.")
    return final_report
