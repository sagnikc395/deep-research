from planner import generate_research_plan
from task_splitter import split_task_into_subtasks
from .prompts import TASK_SPLITTER_SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT
from smolagents import (
    LiteLLMModel,
    ToolCallingAgent,
    MCPClient,
    tool,
    InferenceClientModel,
)
import os
import json
from config import MCP_URL, coordinator_model_id, subagent_model_id


def run_deep_research(query: str) -> str:
    print("\nRunning deep-research ....")

    # generate research plan
    research_plan = generate_research_plan(query)

    # split into explicit subtasks
    subtasks = split_task_into_subtasks(research_plan)

    # coordinator + subagents , using the mcp tools
    print("Initializing coordinator")
    print(f"Coordinator Model: {coordinator_model_id}")
    print(f"Subagent Model: {subagent_model_id}")

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
        # ---- Initialize Subagent TOOL --------------------------------------
        @tool
        def initialize_subagent(
            subtask_id: str, subtask_title: str, subtask_description: str
        ) -> str:
            """
            Spawn a dedicated research sub-agent for a single subtask.

             Args:
                 subtask_id (str): The unique identifier for the subtask.
                 subtask_title (str): The descriptive title of the subtask.
                 subtask_description (str): Detailed instructions for the sub-agent to perform the subtask.

             The sub-agent:
             - Has access to the Firecrawl MCP tools.
             - Must perform deep research ONLY on this subtask.
             - Returns a structured markdown report with:
               - a clear heading identifying the subtask,
               - a narrative explanation,
               - bullet-point key findings,
               - explicit citations / links to sources.
            """
            print(f"Initializing Subagent for task {subtask_id}...")

            subagent = ToolCallingAgent(
                tools=mcp_tools,  # Firecrawl MCP toolkit
                model=subagent_model,
                add_base_tools=False,
                name=f"subagent_{subtask_id}",
            )

            subagent_prompt = subagent_prompt.format(
                user_query=query,
                research_plan=research_plan,
                subtask_id=subtask_id,
                subtask_title=subtask_title,
                subtask_description=subtask_description,
            )

            return subagent.run(subagent_prompt)

        # ---- Coordinator agent ---------------------------------------------
        coordinator = ToolCallingAgent(
            tools=[initialize_subagent],
            model=coordinator_model,
            add_base_tools=False,
            name="coordinator_agent",
        )

        # Coordinator prompt: it gets the list of subtasks and the tool
        subtasks_json = json.dumps(subtasks, indent=2, ensure_ascii=False)

        coordinator_prompt = coordinator_prompt.format(
            user_query=query,
            research_plan=research_plan,
            subtasks_json=subtasks_json,
        )

        final_report = coordinator.run(coordinator_prompt)
        return final_report
