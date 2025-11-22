# Copyright (c) Microsoft. All rights reserved.

import asyncio
import inspect
from agent_framework import HostedWebSearchTool
from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient

try:
    from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
except ImportError:
    AsyncAIProjectClient = None

load_dotenv()

"""
Azure AI Agent With Web Search

This sample demonstrates basic usage of AzureAIClient to create an agent
that can perform web searches using the HostedWebSearchTool.

Pre-requisites:
- Make sure to set up the AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME
  environment variables before running this sample.
"""


def _make_get_openai_client_awaitable(cls) -> None:
    if cls is None:
        return
    original = cls.get_openai_client
    if inspect.iscoroutinefunction(original) or getattr(original, "_agent_framework_async_wrapper", False):
        return

    async def _async_wrapper(self, *args, **kwargs):
        return original(self, *args, **kwargs)

    _async_wrapper._agent_framework_async_wrapper = True  # type: ignore[attr-defined]
    setattr(cls, "get_openai_client", _async_wrapper)  # type: ignore[arg-type]


def _ensure_async_get_openai_client() -> None:
    _make_get_openai_client_awaitable(AIProjectClient)
    _make_get_openai_client_awaitable(AsyncAIProjectClient)


_ensure_async_get_openai_client()


async def main() -> None:
    # Since no Agent ID is provided, the agent will be automatically created.
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="WebsearchAgent",
            instructions="You are a helpful assistant that can search the web",
            tools=[HostedWebSearchTool()],
        ) as agent,
    ):
        query = "What's the weather today in Seattle?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

    """
    Sample output:
    User: What's the weather today in Seattle?
    Agent: Here is the updated weather forecast for Seattle: The current temperature is approximately 57°F,
           mostly cloudy conditions, with light winds and a chance of rain later tonight. Check out more details
           at the [National Weather Service](https://forecast.weather.gov/zipcity.php?inputstring=Seattle%2CWA).
    """


if __name__ == "__main__":
    asyncio.run(main())