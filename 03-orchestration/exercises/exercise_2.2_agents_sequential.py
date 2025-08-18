"""Sequential orchestration using Azure AI Foundry Agents Service (mid‑2025).

This refactors the Semantic Kernel sequential example (exercise_2.1_semantic_kernel_sequential.py)
into a pure Azure AI Foundry Agents pattern for a *deterministic*, fixed-order
pipeline (Concept Extraction -> Copy Writing -> Edit/Polish).

Why not just use Connected Agents?
---------------------------------
Connected Agents let a *primary* agent decide which sub-agents (as tools) to call
and in what order. That is great for *adaptive* planning, but for a strict
sequential pipeline you usually want guaranteed ordering and per‑step control
over retries, timeouts, or structured outputs. The agent service (mid‑2025 GA)
doesn't yet offer a built-in "sequential orchestration" primitive; instead you
compose multiple runs yourself.

Pattern implemented here
------------------------
1. Create 3 specialized agents (concept_extractor, writer, editor) with focused
   instructions.
2. For each step, create a thread, post the previous step's output (seed text
   for the first step is the raw product description), run the agent, and grab
   the final AGENT message text.
3. Pass that text as input to the next step.
4. Print intermediate and final outputs.

Key differences from the SK sample
----------------------------------
SK SequentialOrchestration manages the loop and callbacks; here *you* control
the loop, giving full observability and hook points for production (tracing,
retry, metrics, guardrails, etc.).

Mid‑2025 Azure AI Foundry features leveraged
--------------------------------------------
- GA Agents Service with threads/runs.
- Deterministic multi-agent chaining via explicit run ordering.
- (Optional) Tracing: If APPLICATIONINSIGHTS_CONNECTION_STRING or project
  tracing integration is configured, these runs appear in Tracing.

Environment variables required
------------------------------
- PROJECT_ENDPOINT (or AZURE_AI_PROJECT_ENDPOINT)
- MODEL_DEPLOYMENT_NAME (e.g. gpt-4o-mini)

Usage
-----
python3 exercise_2.2_agents_sequential.py

Cleanup
-------
The script does *not* delete the created agents so you can inspect them; uncomment
the cleanup section if you re-run often.
"""
from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole, ListSortOrder


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def create_specialist_agents(client: AgentsClient, model: str):
    """Create and return the three specialist agents used in the pipeline."""
    concept_extractor = client.create_agent(
        model=model,
        name="concept_extractor_agent",
        instructions=(
            "You are a marketing analyst. Given a product description, identify:\n"
            "Return three clearly labeled sections: Key Features, Target Audience, Unique Selling Points.\n"
            "Keep each bullet concise."
        ),
    )
    writer = client.create_agent(
        model=model,
        name="writer_agent",
        instructions=(
            "You are a marketing copywriter. Given structured feature/audience/USP text, write ~150 words of compelling copy.\n"
            "Return ONLY the copy (single block)."
        ),
    )
    editor = client.create_agent(
        model=model,
        name="editor_agent",
        instructions=(
            "You are an editor. Polish the draft: fix grammar, tighten wording, keep tone persuasive and clear.\n"
            "Return ONLY the final polished copy (single block)."
        ),
    )
    return concept_extractor, writer, editor


def run_single_step(client: AgentsClient, agent_id: str, input_text: str, timeout_seconds: int = 60) -> str:
    """Run one agent on an input payload and return its output text."""
    thread = client.threads.create()
    client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=input_text,
    )
    run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent_id)
    if run.status == "failed":
        raise RuntimeError(f"Run failed for agent {agent_id}: {run.last_error}")
    # Fetch messages ascending, find last AGENT response
    messages = client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    latest: Optional[str] = None
    for m in messages:
        if m.role == MessageRole.AGENT and m.text_messages:
            latest = m.text_messages[-1].text.value
    if not latest:
        raise RuntimeError(f"No agent output found for agent {agent_id}")
    return latest


def print_step(title: str, content: str):
    bar = "-" * len(title)
    print(f"\n{title}\n{bar}\n{content}\n")


def main():
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT") or os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        raise RuntimeError("Set PROJECT_ENDPOINT or AZURE_AI_PROJECT_ENDPOINT")
    model = require_env("MODEL_DEPLOYMENT_NAME")
    credential = DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True)
    client = AgentsClient(endpoint=endpoint, credential=credential)
    product_description = "An eco-friendly stainless steel water bottle that keeps drinks cold for 24 hours"
    with client:
        concept_agent, writer_agent, editor_agent = create_specialist_agents(client, model)
        concepts = run_single_step(client, concept_agent.id, product_description)
        print_step("Concept Extractor Output", concepts)
        draft_copy = run_single_step(client, writer_agent.id, concepts)
        print_step("Writer Draft Output", draft_copy)
        final_copy = run_single_step(client, editor_agent.id, draft_copy)
        print_step("Final Edited Copy", final_copy)
        print("Sequential pipeline complete.")
        # Optional cleanup
        # client.delete_agent(concept_agent.id)
        # client.delete_agent(writer_agent.id)
        # client.delete_agent(editor_agent.id)


if __name__ == "__main__":
    main()
