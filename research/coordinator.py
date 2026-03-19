from .planner import generate_research_plan
from .task_splitter import split_task_into_subtasks
from .prompts import SUBAGENT_PROMPT_TEMPLATE, COORDINATOR_PROMPT_TEMPLATE
from .config import MCP_URL, coordinator_model_id, subagent_model_id
from smolagents import (
    InferenceClientModel,
    ToolCallingAgent,
    MCPClient,
    tool,
)
import os
import json


def run_deep_research(query: str, log=print) -> str:
    log("Running deep-research...")

    log("Generating research plan...")
    research_plan = generate_research_plan(query)
    log("Research plan generated.")

    log("Splitting into subtasks...")
    subtasks = split_task_into_subtasks(research_plan)
    log(f"Generated {len(subtasks)} subtasks.")

    for t in subtasks:
        log(f"  [{t['id']}] {t['title']}")

    log(f"Coordinator Model: {coordinator_model_id}")
    log(f"Subagent Model: {subagent_model_id}")

    coordinator_model = InferenceClientModel(
        model_id=coordinator_model_id,
        api_key=os.environ["HF_TOKEN"],
        provider="novita",
        bill_to="huggingface",
    )
    subagent_model = InferenceClientModel(
        model_id=subagent_model_id,
        api_key=os.environ["HF_TOKEN"],
        provider="novita",
        bill_to="huggingface",
    )

    with MCPClient({"url": MCP_URL, "transport": "streamable-http"}) as mcp_tools:

        @tool
        def initialize_subagent(
            subtask_id: str, subtask_title: str, subtask_description: str
        ) -> str:
            """
            Spawn a dedicated research sub-agent for a single subtask.

            Args:
                subtask_id: The unique identifier for the subtask.
                subtask_title: The descriptive title of the subtask.
                subtask_description: Detailed instructions for the sub-agent.

            The sub-agent has access to the Firecrawl MCP tools and returns
            a structured markdown report for the given subtask.
            """
            log(f"Starting subagent for [{subtask_id}] {subtask_title}...")

            subagent = ToolCallingAgent(
                tools=mcp_tools,
                model=subagent_model,
                add_base_tools=False,
                name=f"subagent_{subtask_id}",
            )

            prompt = SUBAGENT_PROMPT_TEMPLATE.format(
                user_query=query,
                research_plan=research_plan,
                subtask_id=subtask_id,
                subtask_title=subtask_title,
                subtask_description=subtask_description,
            )

            result = subagent.run(prompt)
            log(f"Subagent [{subtask_id}] finished.")
            return result

        coordinator = ToolCallingAgent(
            tools=[initialize_subagent],
            model=coordinator_model,
            add_base_tools=False,
            name="coordinator_agent",
        )

        subtasks_json = json.dumps(subtasks, indent=2, ensure_ascii=False)

        coordinator_prompt = COORDINATOR_PROMPT_TEMPLATE.format(
            user_query=query,
            research_plan=research_plan,
            subtasks_json=subtasks_json,
        )

        log("Coordinator running...")
        final_report = coordinator.run(coordinator_prompt)
        log("Research complete.")
        return final_report
