# deep-research

A multi-agent deep research system built on open-source models. It takes a question, plans an investigation, fans out parallel web-research sub-agents, and stitches their findings into a single polished Markdown report — all from a terminal UI.

Think OpenAI's Deep Research or Perplexity, but local, inspectable, and running entirely on open-source inference.

> For the full motivation and design writeup, see the companion blog post: [Building a Deep Research Agent from Scratch](https://sagnikc395.github.io/projects/deep-research-agent).

## Why

Researching a topic usually means opening thirty tabs, skimming half of them, losing track of what you've already read, and ending up with a scattered pile of notes. Existing "deep research" products solve this but are black boxes — you can't see what they're doing, steer them, or run them locally.

`deep-research` is an attempt to rebuild the core loop — **plan → search → read → synthesize** — as a transparent multi-agent system using entirely open-source models, following the design principles from [Anthropic's multi-agent research system writeup](https://www.anthropic.com/engineering/multi-agent-research-system) and [karpathy/autoresearch](https://github.com/karpathy/autoresearch). The guiding intuition from both: a single agent trying to do everything is worse than multiple specialized agents working in parallel.

## Stack

| Component            | Tool                                                    |
| -------------------- | ------------------------------------------------------- |
| Inference provider   | Hugging Face Inference API (via Novita)                 |
| Agent orchestration  | [smolagents](https://github.com/huggingface/smolagents) |
| Web search & scrape  | [Firecrawl](https://www.firecrawl.dev/) over MCP        |
| UI                   | [Textual](https://textual.textualize.io/) TUI           |
| Package manager      | [uv](https://docs.astral.sh/uv/)                        |

Default models (configurable in `deep-research-config.toml`):

- **Planner** — `deepseek-ai/DeepSeek-V3.2-Exp` (via Together)
- **Coordinator** — `MiniMaxAI/MiniMax-M1-80k`
- **Sub-agents** — `MiniMaxAI/MiniMax-M1-80k`

## Architecture

![deep-research-architecture](./static/deep-research-v0.1.png)

The pipeline has four stages, each a separate concern with a clear interface to the next.

### 1. Planning (`research/planner.py`)

A planner LLM takes the raw user question and produces a **research map** — not just a list of search queries, but a structured outline of the problem space: the key dimensions of the topic, what needs to be understood first, and the likely open questions in the literature. A good research map prevents downstream agents from duplicating work or missing entire angles.

### 2. Splitting (`research/task_splitter.py`)

A splitter LLM decomposes the research map into **non-overlapping subtasks** as structured JSON. Each subtask is scoped tightly enough that a single agent can handle it — one focused question, one thread of investigation. The non-overlap constraint is load-bearing: without it, multiple agents cover the same ground and the final report fills up with redundant summaries.

### 3. Coordinated research (`research/coordinator.py`)

A **coordinator agent** reads the subtask list and spins up one **sub-agent per subtask** via an `initialize_subagent` tool. Each sub-agent is a `ToolCallingAgent` with access to Firecrawl's MCP toolkit, so it can `search`, `scrape`, follow promising links, and return a structured Markdown mini-report — all through native tool calls, no glue code.

Sub-agents run independently with their own context and toolset, so they don't interfere with each other.

### 4. Synthesis

Once every sub-agent reports back, the coordinator stitches the mini-reports into a single coherent Markdown document — reorganizing information, resolving contradictions between sources, and producing something that reads like a real report rather than a concatenation of summaries. The final output is saved to `results.md`.

## Repository layout

```
deep-research/
├── main.py                        # Textual TUI entrypoint
├── deep-research-config.toml      # Model/provider configuration
├── research/
│   ├── coordinator.py             # Orchestrates the full pipeline
│   ├── planner.py                 # Stage 1: research map
│   ├── task_splitter.py           # Stage 2: subtask decomposition
│   ├── prompts.py                 # Prompt templates
│   ├── config.py                  # Config loader (MCP URL, model ids)
│   └── memory.py                  # (v0.2) persistent session memory
├── prompts/                       # Markdown prompt sources
│   ├── planner_system_instructions.md
│   ├── task_splitter_instructions.md
│   ├── coordinator_prompt.md
│   └── subagent_prompt.md
└── static/                        # Architecture diagram
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

This launches a TUI — type your research query, hit Enter, and watch the planner, splitter, coordinator, and sub-agents work in real time. The final report is written to `results.md`.

## Design notes

- **The splitter determines everything.** More time went into tuning the splitting step than any other part of the system. Overlapping subtasks cause redundancy; too-broad ones produce shallow summaries; too-narrow ones miss the bigger picture. Granularity is the main quality lever.
- **Parallel agents need guardrails.** Without constraints, sub-agents will chase the same popular sources. URL-level dedup helps; semantic overlap (different articles saying the same thing) is still an open problem.
- **MCP is underrated as an integration pattern.** Firecrawl exposing search and scraping over MCP meant zero glue code between smolagents and the web. Swap the agent framework tomorrow and the tools still work.
- **Open-source models struggle most at synthesis.** Planning, splitting, searching, and extraction all work well. Weaving ten mini-reports into a cohesive narrative is where the gap with frontier models is most visible — it's the current bottleneck for output quality.

## Roadmap (v0.2)

- [ ] **Memory support** — persistent sessions so the agent can build on previous research instead of starting from scratch every time
- [ ] **Obsidian integration** via [obscure](https://github.com/sagnikc395/obscure) — let the agent scan your vault for open questions and autonomously fill knowledge gaps
- [ ] Cost analysis for a generic run
- [ ] Error detection for infinite loops and token waste

## References

- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- Companion writeup: [Building a Deep Research Agent from Scratch](https://sagnikc395.github.io/projects/deep-research-agent)

## License

MIT — see [LICENSE](./LICENSE).
