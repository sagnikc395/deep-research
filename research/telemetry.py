"""Pipeline telemetry: token-usage tracking and tool-loop detection.

Two concerns are addressed here:

Token waste
-----------
Each pipeline stage records the Agno RunMetrics from the model call.
A per-stage warning fires when a single run exceeds STAGE_TOKEN_WARN
tokens; a pipeline-wide warning fires if the total exceeds
TOTAL_TOKEN_WARN.  A summary table is emitted via PipelineMetrics.report().

Infinite-loop detection
-----------------------
Researcher agents call MCP tools in a loop; Agno's built-in
`tool_call_limit` caps the *total* number of tool calls per run.
check_tool_loop() performs a post-run scan of the ToolExecution list
and warns when the exact same (tool_name, args) pair was repeated more
than REPEATED_CALL_THRESHOLD times, which is the signature of a
stuck agent that keeps retrying the same query.
"""
from __future__ import annotations

import json
import threading
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Optional

# ── Configurable thresholds ───────────────────────────────────────────────────

# Warn if a single stage (one agent.run call) exceeds this many tokens.
STAGE_TOKEN_WARN: int = 30_000

# Warn if the entire pipeline exceeds this many tokens.
TOTAL_TOKEN_WARN: int = 150_000

# Hard cap on tool calls per researcher agent (passed to Agno tool_call_limit).
RESEARCHER_TOOL_CALL_LIMIT: int = 20

# Warn when the same tool+args pair appears this many times in one run.
REPEATED_CALL_THRESHOLD: int = 3


# ── Token tracking ────────────────────────────────────────────────────────────

@dataclass
class _StageStat:
    stage: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class PipelineMetrics:
    """Thread-safe accumulator for token usage across all pipeline stages."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stages: list[_StageStat] = []

    def record(self, stage: str, run_metrics, log: Callable = print) -> None:
        """Record token counts from an Agno ``RunOutput.metrics`` object.

        Silently skips when *run_metrics* is ``None`` (model did not report
        token counts, which happens with some providers).
        """
        if run_metrics is None:
            return
        stat = _StageStat(
            stage=stage,
            input_tokens=run_metrics.input_tokens or 0,
            output_tokens=run_metrics.output_tokens or 0,
            total_tokens=run_metrics.total_tokens or 0,
        )
        with self._lock:
            self._stages.append(stat)

        if stat.total_tokens >= STAGE_TOKEN_WARN:
            log(
                f"[token-warn] '{stage}' consumed {stat.total_tokens:,} tokens "
                f"(in={stat.input_tokens:,}  out={stat.output_tokens:,}) — "
                "consider trimming prompts or capping model output length."
            )

    def report(self, log: Callable = print) -> None:
        """Emit a token-usage summary table via *log*."""
        with self._lock:
            stages = list(self._stages)
        if not stages:
            return

        total_in  = sum(s.input_tokens  for s in stages)
        total_out = sum(s.output_tokens for s in stages)
        total_all = sum(s.total_tokens  for s in stages)

        log("── token usage ─────────────────────────────────────────────────")
        for s in stages:
            log(
                f"  {s.stage:<32}  "
                f"in={s.input_tokens:>8,}  out={s.output_tokens:>8,}  "
                f"total={s.total_tokens:>8,}"
            )
        log(
            f"  {'TOTAL':<32}  "
            f"in={total_in:>8,}  out={total_out:>8,}  total={total_all:>8,}"
        )
        if total_all >= TOTAL_TOKEN_WARN:
            log(
                f"[token-warn] Pipeline consumed {total_all:,} tokens in total. "
                "Review subtask count or prompt verbosity."
            )
        log("────────────────────────────────────────────────────────────────")


# ── Loop detection ────────────────────────────────────────────────────────────

def check_tool_loop(
    tools: Optional[list],
    label: str,
    log: Callable = print,
) -> None:
    """Warn when the same (tool_name, args) pair was called repeatedly.

    *tools* is ``RunOutput.tools`` — a list of ``ToolExecution`` objects.
    *label* identifies which agent/subtask we are inspecting (for the log
    message).  No-ops when *tools* is ``None`` or empty.
    """
    if not tools:
        return

    counts: Counter = Counter()
    for execution in tools:
        name = execution.tool_name or "<unknown>"
        # Normalise args to a stable string so dict key-order doesn't matter.
        try:
            args_key = json.dumps(execution.tool_args or {}, sort_keys=True)
        except (TypeError, ValueError):
            args_key = str(execution.tool_args)
        counts[(name, args_key)] += 1

    for (name, args_key), count in counts.items():
        if count >= REPEATED_CALL_THRESHOLD:
            log(
                f"[loop-warn] {label}: tool '{name}' was called {count}× with "
                f"identical args — the agent may be stuck in a loop.\n"
                f"  args: {args_key[:120]}"
            )
