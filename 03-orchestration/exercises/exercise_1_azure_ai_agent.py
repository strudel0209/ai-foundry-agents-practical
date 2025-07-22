# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread

"""
The following sample demonstrates how to create an Azure AI agent that answers
user questions. This sample demonstrates the basic steps to create an agent
and simulate a conversation with the agent.

The interaction with the agent is via the `get_response` method, which sends a
user input to the agent and receives a response from the agent. The conversation
history is maintained by the agent service, i.e. the responses are automatically
associated with the thread. Therefore, client code does not need to maintain the
conversation history.
"""

# Load environment variables
load_dotenv()

# Simulate a conversation with the agent
USER_INPUTS = [
    "Hello, I am John Doe.",
    "What is your name?",
    "What is my name?",
]


async def main() -> None:
    # Load configuration from environment variables
    endpoint = os.getenv("PROJECT_ENDPOINT")
    project_name = os.getenv("PROJECT_NAME")
    model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    # Validate required environment variables
    if not endpoint or not project_name:
        raise ValueError("PROJECT_ENDPOINT and PROJECT_NAME environment variables must be set")
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(
            credential=creds,
            endpoint=endpoint,
            project_name=project_name,
            model_deployment_name=model_deployment_name
        ) as client,
    ):
        # Check if an agent with the name "Assistant" already exists
        agent_definition = None
        try:
            # List existing agents and find one named "Assistant"
            agents = await client.agents.list_agents()
            async for agent in agents:
                if agent.name == "Assistant":
                    agent_definition = agent
                    print(f"Using existing agent: {agent.id}")
                    break
        except Exception as e:
            print(f"Could not list agents: {e}")
        
        # If no existing agent found, create a new one
        if agent_definition is None:
            # 1. Create an agent on the Azure AI agent service
            agent_definition = await client.agents.create_agent(
                model=model_deployment_name,
                name="Assistant",
                instructions="Answer the user's questions.",
            )
            print(f"Created new agent: {agent_definition.id}")

        # 2. Create a Semantic Kernel agent wrapper for the Azure AI agent
        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
        )

        # 3. Create a thread for the agent
        # If no thread is provided, a new thread will be
        # created and returned with the initial response
        thread: AzureAIAgentThread = None

        try:
            for user_input in USER_INPUTS:
                print(f"# User: {user_input}")
                # 4. Invoke the agent with the specified message for response
                response = await agent.get_response(messages=user_input, thread=thread)
                print(f"# {response.name}: {response}")
                thread = response.thread

        finally:
            # 6. Cleanup: Delete the thread and agent (commented out to preserve resources)
            # await thread.delete() if thread else None
            # await client.agents.delete_agent(agent.id)
            print(f"\nAgent ID: {agent.id}")
            print(f"Thread ID: {thread.id if thread else 'None'}")
            print("Resources preserved for future use.")

if __name__ == "__main__":
    asyncio.run(main())