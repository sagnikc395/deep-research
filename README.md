
# deep-research

A multi-agent deep research system built on open-source models.

| Component | Tool |
|---|---|
| Inference Provider | Hugging Face |
| Web Search | Firecrawl MCP |
| Agent Coordination | smolagents |

## Architecture

![deep-research-architecture](./static/deep-research-v0.1.png)

### User Flow

1. The user types a question in the CLI
2. A **planner LLM** drafts a thorough research map
3. A **splitter LLM** turns that map into bite-sized, non-overlapping subtasks in JSON
4. A **coordinator agent** spins up one sub-agent per subtask — each sub-agent can search and scrape the web via Firecrawl's MCP toolkit
5. The coordinator stitches every mini-report into one polished Markdown file

## Setup & Configuration

### Prerequisites

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (recommended package manager)
- A [Hugging Face](https://huggingface.co/) account and API token
- A [Firecrawl](https://www.firecrawl.dev/) API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/<your-username>/deep-research.git
cd deep-research
```

2. Install dependencies:
```bash
uv sync
```

3. Copy the sample env file and fill in your keys:
```bash
cp .env.sample .env
```

Then edit `.env` with your credentials:
```
HF_TOKEN="your-huggingface-token"
FIRECRAWL_API_KEY="your-firecrawl-api-key"
```

### Running

```bash
uv run python main.py
```

This launches a TUI where you can type your research query. Results are saved to `results.md`.

## Roadmap (v0.2)

- [ ] Memory support
- [ ] Obsidian CLI integration for autonomous topic discovery
- [ ] Cost analysis for a generic run
- [ ] Error detection for infinite loops and token waste

## References

- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [autoresearch](https://github.com/karpathy/autoresearch)
