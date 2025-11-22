# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from typing import Any

from agent_framework import ChatMessage, ConcurrentBuilder
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
load_dotenv()

"""
Sample: Concurrent fan-out/fan-in (agent-only API) with default aggregator

Build a high-level concurrent workflow using ConcurrentBuilder and three domain agents.
The default dispatcher fans out the same user prompt to all agents in parallel.
The default aggregator fans in their results and yields output containing
a list[ChatMessage] representing the concatenated conversations from all agents.

Demonstrates:
- Minimal wiring with ConcurrentBuilder().participants([...]).build()
- Fan-out to multiple agents, fan-in aggregation of final ChatMessages
- Workflow completion when idle with no pending work

Prerequisites:
- Azure OpenAI access configured for AzureOpenAIChatClient (use az login + env vars)
- Familiarity with Workflow events (AgentRunEvent, WorkflowOutputEvent)
"""


async def main() -> None:
    # 1) Create three domain agents using AzureOpenAIChatClient
    chat_client = AzureOpenAIChatClient(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

    researcher = chat_client.create_agent(
        instructions=(
            "You're an expert market and product researcher. Given a prompt, provide concise, factual insights,"
            " opportunities, and risks."
        ),
        name="researcher",
    )

    marketer = chat_client.create_agent(
        instructions=(
            "You're a creative marketing strategist. Craft compelling value propositions and target messaging"
            " aligned to the prompt."
        ),
        name="marketer",
    )

    legal = chat_client.create_agent(
        instructions=(
            "You're a cautious legal/compliance reviewer. Highlight constraints, disclaimers, and policy concerns"
            " based on the prompt."
        ),
        name="legal",
    )

    # 2) Build a concurrent workflow
    workflow = ConcurrentBuilder().participants([researcher, marketer, legal]).build()

    # 3) Interactive loop
    print("=" * 70)
    print("Concurrent Agents System - Interactive Mode")
    print("=" * 70)
    print("\nThree agents will analyze your input concurrently:")
    print("  • Researcher: Market insights and analysis")
    print("  • Marketer: Creative strategies and messaging")
    print("  • Legal: Compliance and risk assessment")
    print("\nType 'exit' or 'quit' to end the session.\n")
    
    while True:
        # Get user input
        user_prompt = input("Enter your prompt: ").strip()
        
        # Check for exit conditions
        if user_prompt.lower() in ['exit', 'quit', '']:
            print("\nGoodbye!")
            break
        
        print("\n" + "=" * 70)
        print("Processing your request...")
        print("=" * 70)
        
        try:
            # Run the workflow with user's prompt
            events = await workflow.run(user_prompt)
            outputs = events.get_outputs()

            if outputs:
                print("\n===== Final Aggregated Conversation (messages) =====")
                for output in outputs:
                    messages: list[ChatMessage] | Any = output
                    for i, msg in enumerate(messages, start=1):
                        name = msg.author_name if msg.author_name else "user"
                        print(f"\n{'-' * 60}\n{i:02d} [{name}]:\n{msg.text}")
            else:
                print("\nNo output received from agents.")
                
            print("\n" + "=" * 70)
            print("Ready for next prompt")
            print("=" * 70 + "\n")
            
        except Exception as e:
            print(f"\nError processing request: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    asyncio.run(main())