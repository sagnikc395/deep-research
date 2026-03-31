# deep-research

an implementation of a multi-agent deep research system
using open-source models.

- inference provider: huuggingface
- web search : firecrawl mcp
- agent coordination: smolagents

## architecture

![deep-research-architecture](./static/deep-research-v0.1.png)

### explanation of user flow

- User wil type a question in the CLI
- a planner LLM will draft a thorough research map
- a splitter LLM will then turn that map into bite-sized, non-overlapping subtasks in JSON
- a coordinator agent spins up one sub-agent per subtask - every sub-agent can search and scrape the web through Firecrawl's MCP toolkit
- the coordinator stitches every mini-report into one polished markdown file.

## setup and configuration

### prerequisites

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (recommended package manager)
- A [Hugging Face](https://huggingface.co/) account and API token
- A [Firecrawl](https://www.firecrawl.dev/) API key

### installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/deep-research.git
cd deep-research
```

2. Install dependencies with uv:

```bash
uv sync
```

3. Copy the sample env file and fill in your keys:

```bash
cp .env.sample .env
```

Edit `.env` and set your credentials:

```
HF_TOKEN="your-huggingface-token"
FIRECRAWL_API_KEY="your-firecrawl-api-key"
```

### running

```bash
uv run python main.py
```

This launches a TUI where you can type your research query. Results are saved to `results.md`.

## todo

- [v0.2] add support for memory
- [v0.2] using obscure cli to interact with obsidian to autonomously search for research topics
- [v0.2] Add support for cost analysis for a generic run
- [v0.2] Error detection for infinite loops or when tokens are being wasted

## references

- [Anthropic - How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [autoresearch](https://github.com/karpathy/autoresearch)
