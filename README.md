# deep-research

A multi-agent deep research system built on open-source models. It takes a question, plans an investigation, fans out web-research sub-agents, and stitches their findings into a single polished Markdown report — all from a terminal UI.

Think OpenAI's Deep Research or Perplexity, but local, inspectable, and running entirely on open-source inference.

> For the full motivation and design writeup, see the companion blog post: [Building a Deep Research Agent from Scratch](https://sagnikc395.github.io/projects/deep-research-agent).

## Why

Researching a topic usually means opening thirty tabs, skimming half of them, losing track of what you've already read, and ending up with a scattered pile of notes. Existing "deep research" products solve this but are black boxes — you can't see what they're doing, steer them, or run them locally.

`deep-research` is an attempt to rebuild the core loop — **plan → search → read → synthesize** — as a transparent multi-agent system using entirely open-source models, following the design principles from [Anthropic's multi-agent research system writeup](https://www.anthropic.com/engineering/multi-agent-research-system) and [karpathy/autoresearch](https://github.com/karpathy/autoresearch). The guiding intuition from both: a single agent trying to do everything is worse than multiple specialized agents working in parallel.

## Stack

| Component            | Tool                                             |
| -------------------- | ------------------------------------------------ |
| Inference provider   | Hugging Face Inference API (Novita, Together)    |
| Agent framework      | [Agno](https://github.com/agno-agi/agno)         |
| Web search & scrape  | [Firecrawl](https://www.firecrawl.dev/) over MCP |
| UI                   | [Textual](https://textual.textualize.io/) TUI    |
| Package manager      | [uv](https://docs.astral.sh/uv/)                 |

Default models (configurable in `deep-research-config.toml`):

- **Planner** — `deepseek-ai/DeepSeek-V3.2-Exp` (via Together)
- **Task splitter** — `deepseek-ai/DeepSeek-V3.2-Exp` (via Together)
- **Researchers / Synthesizer** — `MiniMaxAI/MiniMax-M1-80k` (via Novita)

## Architecture

![deep-research-architecture](./static/deep-research-v0.1.png)

The pipeline has four stages, each a separate module with a clear interface to the next.

### 1. Planning (`research/planner.py`)

A planner Agno Agent takes the raw user question and produces a **research map** — a structured outline of the problem space: the key dimensions of the topic, what needs to be understood first, and the likely open questions. Relevant past sessions from memory are prepended as context so the agent can build on prior work.

### 2. Splitting (`research/task_splitter.py`)

A splitter Agno Agent decomposes the research map into **non-overlapping subtasks** using Pydantic structured output (`response_model=SubtaskList`). Each subtask is scoped tightly enough that a single agent can handle it. The non-overlap constraint is load-bearing: without it, multiple agents cover the same ground and the final report fills up with redundant summaries.

### 3. Research (`research/researcher.py`)

One **researcher agent** is spawned per subtask. Each researcher is an Agno Agent with access to Firecrawl's MCP toolkit, so it can search, scrape, follow promising links, and return a structured Markdown mini-report through native tool calls.

MCP requires an async transport (SSE / websocket). To stay compatible with the sync pipeline, each researcher runs in its own OS thread via `ThreadPoolExecutor` so that `asyncio.run()` always gets a clean event loop.

### 4. Synthesis (`research/coordinator.py`)

Once every researcher reports back, a synthesizer Agno Agent weaves the mini-reports into a single coherent Markdown document — reorganizing information, resolving contradictions, and producing something that reads like a real report rather than a concatenation of summaries. The final output is saved to `results.md`.

## Repository layout

```
deep-research/
├── main.py                          # Textual TUI entrypoint
├── deep-research-config.toml        # Model / provider configuration
├── research/
│   ├── models.py                    # Agno model factory (hf_model)
│   ├── coordinator.py               # Pipeline orchestrator
│   ├── planner.py                   # Stage 1: research map
│   ├── task_splitter.py             # Stage 2: subtask decomposition
│   ├── researcher.py                # Stage 3: per-subtask research agent
│   ├── prompts.py                   # Prompt template loader
│   ├── config.py                    # Config loader (MCP URL, model ids)
│   └── memory.py                    # Persistent session memory (SQLite)
├── prompts/
│   ├── planner_system_instructions.md
│   ├── task_splitter_instructions.md
│   ├── subagent_prompt.md
│   ├── coordinator_prompt.md
│   └── synthesis_prompt.md
└── static/
```

## Setup

### Prerequisites

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)
- A [Hugging Face](https://huggingface.co/) account and API token
- A [Firecrawl](https://www.firecrawl.dev/) API key

### Installation

```bash
git clone https://github.com/sagnikc395/deep-research.git
cd deep-research
uv sync
cp .env.sample .env
```

Then fill in `.env`:

```
HF_TOKEN="your-huggingface-token"
FIRECRAWL_API_KEY="your-firecrawl-api-key"
```

### Running

```bash
uv run python main.py
```

This launches a TUI — type your research query, hit Enter, and watch the planner, splitter, researchers, and synthesizer work in real time. The final report is written to `results.md`.

## Configuration

All models and providers are set in `deep-research-config.toml`:

```toml
[app]
task_planner_model_id  = "deepseek-ai/DeepSeek-V3.2-Exp"
task_planner_provider  = "together"
coordinator_model_id   = "MiniMaxAI/MiniMax-M1-80k"
coordinator_provider   = "novita"
subagent_model_id      = "MiniMaxAI/MiniMax-M1-80k"
subagent_provider      = "novita"
```

Supported provider values: `"novita"`, `"together"`, `"auto"` (HF default routing).

## Design notes

- **The splitter determines everything.** More time went into tuning the splitting step than any other part of the system. Overlapping subtasks cause redundancy; too-broad ones produce shallow summaries; too-narrow ones miss the bigger picture. Granularity is the main quality lever.
- **Parallel agents need guardrails.** Without constraints, sub-agents will chase the same popular sources. URL-level dedup helps; semantic overlap (different articles saying the same thing) is still an open problem.
- **MCP is underrated as an integration pattern.** Firecrawl exposing search and scraping over MCP meant zero glue code between the agent framework and the web. Swap the agent framework tomorrow and the tools still work.
- **Open-source models struggle most at synthesis.** Planning, splitting, searching, and extraction all work well. Weaving ten mini-reports into a cohesive narrative is where the gap with frontier models is most visible — it's the current bottleneck for output quality.
- **Coordinator as plain Python.** The original design used an LLM-as-coordinator pattern where the coordinator would invoke sub-agents via a tool. The current design replaces that with a Python loop, which is simpler, deterministic, and easier to reason about. The LLM is now only used where it adds real value.

## Roadmap

- [x] **Memory support** — persistent sessions so the agent can build on previous research
- [ ] **Parallel researchers** — run subtask agents concurrently instead of sequentially
- [ ] **Obsidian integration** via [obscure](https://github.com/sagnikc395/obscure) — let the agent scan your vault for open questions and autonomously fill knowledge gaps
- [ ] Cost tracking per run
- [ ] Error detection for infinite loops and token waste

## References

- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- Companion writeup: [Building a Deep Research Agent from Scratch](https://sagnikc395.github.io/projects/deep-research-agent)

## License

MIT — see [LICENSE](./LICENSE).
