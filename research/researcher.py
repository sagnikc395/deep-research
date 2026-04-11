"""Stage 3 — Single-subtask researcher.

Spawns an Agno Agent with Firecrawl MCP tools to research one subtask.

MCP requires an async context (websocket / SSE transport). To stay
compatible with sync callers (including Textual thread workers that
may already have a running event loop), each subtask is executed in a
fresh OS thread via ThreadPoolExecutor so that asyncio.run() always
gets a clean loop.
"""
import asyncio
import concurrent.futures

from agno.agent import Agent
from agno.tools.mcp import MCPTools

from .config import MCP_URL, subagent_model_id, subagent_provider
from .models import hf_model
from .prompts import SUBAGENT_PROMPT_TEMPLATE


async def _run_async(prompt: str) -> str:
    """Run the research agent inside an async MCP context."""
    async with MCPTools(url=MCP_URL, transport="streamable-http") as mcp:
        agent = Agent(
            model=hf_model(subagent_model_id, subagent_provider),
            tools=[mcp],
            markdown=True,
        )
        response = await agent.arun(prompt)
        return response.content


def research_subtask(
    query: str,
    plan: str,
    subtask: dict,
    log=print,
) -> str:
    """Research *subtask* and return a markdown report.

    Runs asynchronous MCP operations in an isolated thread so the
    caller can be either sync or inside an existing event loop.
    """
    log(f"Researcher starting [{subtask['id']}] {subtask['title']}...")

    prompt = SUBAGENT_PROMPT_TEMPLATE.format(
        user_query=query,
        research_plan=plan,
        subtask_id=subtask["id"],
        subtask_title=subtask["title"],
        subtask_description=subtask["description"],
    )

    # ThreadPoolExecutor gives us a thread with no running event loop,
    # so asyncio.run() always works regardless of the caller context.
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, _run_async(prompt))
        result = future.result()

    log(f"Researcher [{subtask['id']}] done.")
    return result
