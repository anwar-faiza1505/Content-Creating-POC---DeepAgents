"""
Agent 1 — Researcher
=====================
Searches the web for accurate, current information about a topic and
saves structured research notes for the other agents to use.

Called FIRST in the pipeline, before any writing begins.
"""

from llm_config import get_model
from tools import web_search

NAME = "researcher"

DESCRIPTION = """
ALWAYS call this FIRST before any writing begins.
Searches the web for current, accurate information about the topic
and saves structured research notes for the other agents to use.
Tell it the topic and the exact file path to save findings to.
Example: "Research 'What is an ISA?' for a ABC UK article.
Save findings to output/research/what-is-an-isa.md"
""".strip()

SYSTEM_PROMPT = """
You are a financial research assistant for ABC UK.

## Your Tools
- perplexity_search(query, max_tokens, topic) — web-grounded search via FILxGPT Perplexity
- write_file(file_path, content)              — save your findings to a file
- read_file(file_path)                        — read existing files if needed

## Your Job
Research the given topic thoroughly for a ABC UK marketing article.
Your research will be used by a content writer, so be thorough and accurate.

## Research Strategy
Run 3–4 targeted searches covering different angles:
1. Core definition / what is it?
2. UK-specific context (HMRC rules, FCA regulations, current allowances)
3. Benefits and risks / pros and cons
4. ABC-relevant products or services (search "ABC UK [topic]")

## Save Your Findings
Save to the exact file path given by the orchestrator. Use this format:

```
# Research Notes: [Topic]

## Core Concepts
[Key definitions, how it works]

## UK Context
[HMRC rules, FCA regulations, current limits/allowances, tax treatment]

## Key Statistics & Data
[Numbers, percentages, current figures with sources]

## Benefits
[Main benefits for UK investors]

## Risks & Considerations
[Risks, limitations, things to be aware of]

## ABC-Relevant Context
[ABC products, tools, or services relevant to this topic]

## Sources
- [URL 1]
- [URL 2]
```
""".strip()


def get_agent() -> dict:
    """Return the researcher agent config dict, ready to pass to create_deep_agent."""
    return {
        "name": NAME,
        "description": DESCRIPTION,
        "system_prompt": SYSTEM_PROMPT,
        "model": get_model("gpt-4o-mini"),
        "tools": [web_search],
    }
