#!/usr/bin/env python3
"""
ABC Content Writing — Multi-Agent Orchestration POC
=========================================================

HOW IT WORKS:
  You provide a topic. The orchestrator delegates to 4 specialist agents
  that run in sequence, each building on the previous one's output:

    1. Researcher      → searches the web, saves research notes
    2. Outline Writer  → reads research, structures the article
    3. Content Writer  → reads outline + research, writes the draft
    4. Compliance Editor → adds FCA disclaimers, produces final article

USAGE:
    python run.py                               # asks for topic interactively
    python run.py "What is a Stocks and Shares ISA?"
    python run.py "How to start investing with small amounts"
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
import os

os.environ["OPENAI_API_KEY"] = "dummy"
load_dotenv(Path(__file__).parent / ".env")

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner

from deepagents import create_deep_agent, FilesystemPermission
from deepagents.backends import FilesystemBackend

from llm_config import get_model
from agents.researcher import get_agent as researcher_agent
from agents.outline_writer import get_agent as outline_writer_agent
from agents.content_writer import get_agent as content_writer_agent
from agents.compliance_editor import get_agent as compliance_editor_agent

#

from opentelemetry import trace
from fil_aiobs.telemetry import init_otel

from opentelemetry.instrumentation.langchain import LangchainInstrumentor

LANGSMITH_PROJECT_API_KEY = os.getenv("LANGSMITH_PROJECT_API_KEY")

# Initialize OTEL SDK
provider = init_otel(
    endpoint="https://fil-ai-observability-uat.k8s.npiek8sinfra1np1.npaws.ukfilcld/api/v1/otel",
    x_api_key=LANGSMITH_PROJECT_API_KEY,
    project_name="deepagents",
    service_name="deepagents-memory",
    resource_attributes={
        "component": "langgraph",
    },
)
tracer = trace.get_tracer(__name__)
LangchainInstrumentor().instrument(
    tracer_provider=provider,
)

#
# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

POC_DIR = Path(__file__).parent
console = Console()

# Ensure output subdirectories exist — FilesystemBackend won't create them automatically
for _subdir in ("output/research", "output/outlines", "output/drafts", "output/final"):
    (POC_DIR / _subdir).mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Agent factory
# Creates the orchestrator agent with memory, skills, and subagents
# ---------------------------------------------------------------------------


def create_content_agent():
    """Build the content writing orchestrator.

    What each argument does:
      model       → the LLM powering the orchestrator
      memory      → AGENTS.md is loaded into the orchestrator's context
                    (brand voice, style guide, content pillars)
      skills      → skills/ABC-article/SKILL.md tells the orchestrator
                    the step-by-step workflow to follow
      subagents   → 4 specialist agents, one Python file each in agents/
      backend     → FilesystemBackend with virtual_mode=True so all paths
                    like /output/... resolve under POC_DIR on disk
      permissions → explicit allow/deny rules:
                    - allow read anywhere (agents need to read AGENTS.md, skills, output files)
                    - allow write only inside /output/ (research, outlines, drafts, final)
                    - deny write everywhere else (prevents accidental overwrites)
    """
    return create_deep_agent(
        model=get_model("gpt-4o"),  # Main orchestrator model
        memory=["./AGENTS.md"],  # Brand voice & style guide
        skills=["./skills/"],  # Article writing workflow
        tools=[],  # Orchestrator delegates; no direct tools
        subagents=[
            researcher_agent(),
            outline_writer_agent(),
            content_writer_agent(),
            compliance_editor_agent(),
        ],
        backend=FilesystemBackend(root_dir=POC_DIR, virtual_mode=True),
        permissions=[
            # Allow agents to read anything inside the POC directory
            FilesystemPermission(operations=["read"], paths=["/**"], mode="allow"),
            # Allow agents to write ONLY inside /output/
            FilesystemPermission(
                operations=["write"], paths=["/output/**"], mode="allow"
            ),
            # Deny writes everywhere else
            FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
        ],
    )


# ---------------------------------------------------------------------------
# Display — makes the multi-agent pipeline visible as it runs
# ---------------------------------------------------------------------------

# Labels for each agent (shown in the terminal as agents activate)
AGENT_LABELS = {
    "researcher": "[bold cyan]Researcher[/bold cyan]",
    "outline_writer": "[bold yellow]Outline Writer[/bold yellow]",
    "content_writer": "[bold green]Content Writer[/bold green]",
    "compliance_editor": "[bold magenta]Compliance Editor[/bold magenta]",
}


def print_message(msg):
    """Render an agent message with formatting that shows the pipeline flow."""

    if isinstance(msg, HumanMessage):
        console.print(
            Panel(
                str(msg.content),
                title="[bold blue]Your Request[/bold blue]",
                border_style="blue",
            )
        )

    elif isinstance(msg, AIMessage):
        # Extract text — content can be a string or a list of typed parts
        content = msg.content
        if isinstance(content, list):
            content = "\n".join(
                p.get("text", "")
                for p in content
                if isinstance(p, dict) and p.get("type") == "text"
            )
        if content and content.strip():
            console.print(
                Panel(
                    Markdown(content.strip()),
                    title="[bold blue]Orchestrator[/bold blue]",
                    border_style="blue",
                )
            )

        # Show when the orchestrator delegates to a specialist agent
        for tc in (
            msg.tool_calls if hasattr(msg, "tool_calls") and msg.tool_calls else []
        ):
            if tc.get("name") == "task":
                agent_type = tc.get("args", {}).get("subagent_type", "subagent")
                label = AGENT_LABELS.get(agent_type, f"[bold]{agent_type}[/bold]")
                first_line = (
                    tc.get("args", {})
                    .get("description", "")
                    .strip()
                    .split("\n")[0][:80]
                )
                console.print(f"\n[dim]┌─ Delegating to[/dim] {label}")
                console.print(f"[dim]│  Task: {first_line}...[/dim]")

    elif isinstance(msg, ToolMessage):
        label = AGENT_LABELS.get(
            getattr(msg, "name", "subagent"),
            f"[bold]{getattr(msg, 'name', 'subagent')}[/bold]",
        )
        console.print(f"[dim]└─ ✓ {label} completed[/dim]\n")


def show_pipeline_banner(topic: str):
    """Print the pipeline overview before starting."""
    console.print()
    console.print(
        Panel(
            f"[bold]Topic:[/bold] [italic]{topic}[/italic]\n\n"
            "[dim]Four agents will work in sequence:[/dim]\n\n"
            "  [cyan]1. Researcher[/cyan]        → gathers topic knowledge from the web\n"
            "  [yellow]2. Outline Writer[/yellow]    → structures the article (ABC format)\n"
            "  [green]3. Content Writer[/green]    → writes the full article (800–1200 words)\n"
            "  [magenta]4. Compliance Editor[/magenta] → adds FCA disclaimers & finalises\n\n"
            "[dim]Watch the pipeline run below ↓[/dim]",
            title="[bold blue]ABC Content Pipeline — Multi-Agent Orchestration[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
    )
    console.print()


# ---------------------------------------------------------------------------
# Main pipeline runner
# ---------------------------------------------------------------------------


async def run_pipeline(topic: str):
    """Run the full multi-agent content creation pipeline for a given topic."""
    show_pipeline_banner(topic)

    agent = create_content_agent()
    slug = (
        topic.lower()
        .strip()
        .replace(" ", "-")
        .replace("?", "")
        .replace("'", "")
        .replace(":", "")[:60]
    )

    task_prompt = (
        f"Write a ABC-standard marketing article about: **{topic}**\n"
        f"Use the slug `{slug}` for all output file names.\n"
        "Follow the ABC-article skill: researcher → outline_writer → content_writer → compliance_editor.\n"
        "After all 4 steps, confirm the final file path and give a 2-sentence summary."
    )

    messages = [HumanMessage(content=task_prompt)]
    printed_count = 0

    with Live(
        Spinner("dots", text="[dim]Pipeline running...[/dim]"),
        console=console,
        refresh_per_second=10,
    ) as live:
        async for state in agent.astream(
            {"messages": messages},
            stream_mode="values",
            config={"configurable": {"thread_id": f"ABC-poc-{slug}"}},
        ):
            for msg in state.get("messages", [])[printed_count:]:
                live.stop()
                print_message(msg)
                live.start()
                printed_count += 1

    console.print()
    console.print(
        Panel(
            f"[bold green]Pipeline complete![/bold green]\n\nYour article: [cyan]output/final/{slug}.md[/cyan]",
            title="Done",
            border_style="green",
        )
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    console.print("\n[bold blue]ABC Marketing Content Generator[/bold blue]")
    console.print("[dim]Multi-agent orchestration powered by DeepAgents[/dim]\n")

    topic = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else console.input("[bold]Enter your article topic:[/bold] ").strip()
    )
    if not topic:
        console.print("[red]No topic provided. Exiting.[/red]")
        sys.exit(1)

    asyncio.run(run_pipeline(topic))


if __name__ == "__main__":
    main()
