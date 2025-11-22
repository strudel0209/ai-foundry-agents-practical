import asyncio
import os
from typing import cast

from agent_framework import ChatMessage, Role, SequentialBuilder, WorkflowOutputEvent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
load_dotenv()

"""
Sample: Sequential workflow (agent-focused API) with shared conversation context

Build a high-level sequential workflow using SequentialBuilder and two domain agents.
The shared conversation (list[ChatMessage]) flows through each participant. Each agent
appends its assistant message to the context. The workflow outputs the final conversation
list when complete.

Note on internal adapters:
- Sequential orchestration includes small adapter nodes for input normalization
  ("input-conversation"), agent-response conversion ("to-conversation:<participant>"),
  and completion ("complete"). These may appear as ExecutorInvoke/Completed events in
  the stream—similar to how concurrent orchestration includes a dispatcher/aggregator.
  You can safely ignore them when focusing on agent progress.

Prerequisites:
- Azure OpenAI access configured for AzureOpenAIChatClient (use az login + env vars)
"""


async def main() -> None:
    # 1) Create agents
    chat_client = AzureOpenAIChatClient(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

    writer = chat_client.create_agent(
        instructions=("You are a concise copywriter. Provide a single, punchy marketing sentence based on the prompt."),
        name="writer",
    )

    reviewer = chat_client.create_agent(
        instructions=("You are a thoughtful reviewer. Give brief feedback on the previous assistant message."),
        name="reviewer",
    )

    # 2) Build sequential workflow: writer -> reviewer
    workflow = SequentialBuilder().participants([writer, reviewer]).build()

    # 3) Interactive loop
    print("=" * 70)
    print("Sequential Agents System - Interactive Mode")
    print("=" * 70)
    print("\nTwo agents will work on your input sequentially:")
    print("  1. Writer: Creates a punchy marketing sentence")
    print("  2. Reviewer: Provides feedback on the writer's output")
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
            # Run and collect outputs
            outputs: list[list[ChatMessage]] = []
            async for event in workflow.run_stream(user_prompt):
                if isinstance(event, WorkflowOutputEvent):
                    outputs.append(cast(list[ChatMessage], event.data))

            if outputs:
                print("\n===== Final Conversation =====")
                for i, msg in enumerate(outputs[-1], start=1):
                    name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
                    print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")
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