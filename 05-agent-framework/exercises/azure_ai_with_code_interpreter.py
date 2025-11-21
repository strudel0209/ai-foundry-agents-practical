# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework import AgentRunResponse, ChatResponseUpdate, HostedCodeInterpreterTool
from agent_framework.azure import AzureAIAgentClient
from azure.ai.agents.models import (
    RunStepDeltaCodeInterpreterDetailItemObject,
)
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential as SyncAzureCliCredential
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv
load_dotenv()

"""
Azure AI Agent with Code Interpreter Example

This sample demonstrates using HostedCodeInterpreterTool with Azure AI Agents
for Python code execution and mathematical problem solving.
"""


def print_code_interpreter_inputs(response: AgentRunResponse) -> None:
    """Helper method to access code interpreter data."""

    print("\nCode Interpreter Inputs during the run:")
    if response.raw_representation is None:
        return
    for chunk in response.raw_representation:
        if isinstance(chunk, ChatResponseUpdate) and isinstance(
            chunk.raw_representation, RunStepDeltaCodeInterpreterDetailItemObject
        ):
            print(chunk.raw_representation.input, end="")
    print("\n")


async def main() -> None:
    """Example showing how to use the HostedCodeInterpreterTool with Azure AI."""
    print("=== Azure AI Agent with Code Interpreter Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as chat_client,
    ):
        agent = chat_client.create_agent(
            name="CodingAgent",
            instructions="""
You are a data analyst that helps with data processing, analysis, and visualization.

Your capabilities:
- Analyze datasets and provide insights
- Create visualizations using matplotlib/seaborn
- Perform statistical calculations
- Generate reports with findings

When given data tasks:
1. Write clean, well-commented Python code
2. Create meaningful visualizations
3. Explain your analysis approach
4. Provide actionable insights
5. Save any charts or outputs as files to the current working directory
""",
            tools=HostedCodeInterpreterTool(),
        )
        # Analysis tasks
        tasks = [
            {
                'name': 'Sales Analysis',
                'description': '''
Analyze sales data and create visualizations:

Create a dataset with monthly sales data for Q4 2024:
- October: $125,000
- November: $140,000  
- December: $180,000

Tasks:
1. Calculate total sales and growth rates
2. Create a bar chart showing monthly sales
3. Create a line chart showing the trend
4. Calculate average monthly sales
5. Provide insights about the sales performance
'''
            },
            {
                'name': 'Statistical Analysis',
                'description': '''
Perform statistical analysis on customer satisfaction scores:

Data: [8.5, 7.2, 9.1, 6.8, 8.9, 7.5, 8.2, 9.3, 7.8, 8.6, 9.0, 7.9, 8.4, 8.8, 7.6]

Tasks:
1. Calculate basic statistics (mean, median, std dev)
2. Create a histogram of the scores
3. Identify any outliers
4. Determine if scores follow normal distribution
5. Provide recommendations based on the analysis
'''
            },
            {
                'name': 'Data Comparison',
                'description': '''
Compare performance between two products:

Product A sales: [45, 52, 48, 61, 58, 55, 49, 63, 57, 51]
Product B sales: [38, 41, 44, 39, 46, 42, 40, 47, 43, 45]

Tasks:
1. Calculate summary statistics for both products
2. Create a comparison chart
3. Perform a t-test to check for significant difference
4. Visualize the distributions
5. Recommend which product is performing better
'''
            }
        ]

        # Initialize project client for file operations
        project_client = AIProjectClient(
            endpoint=os.getenv("PROJECT_ENDPOINT"),
            credential=SyncAzureCliCredential(),
        )

        for i, task in enumerate(tasks, 1):
            print(f"\n--- Task {i}: {task['name']} ---")
            query = task['description']
            print(f"User: {query}")
            response = await AgentRunResponse.from_agent_response_generator(agent.run_stream(query))
            print(f"Agent: {response}")
            
            # Check for generated files in the response
            if response.raw_representation:
                file_count = 0
                for chunk in response.raw_representation:
                    if isinstance(chunk, ChatResponseUpdate) and isinstance(
                        chunk.raw_representation, RunStepDeltaCodeInterpreterDetailItemObject
                    ):
                        if hasattr(chunk.raw_representation, 'outputs') and chunk.raw_representation.outputs:
                            for output in chunk.raw_representation.outputs:
                                if hasattr(output, 'image') and output.image:
                                    file_id = output.image.file_id
                                    file_count += 1
                                    # Ensure output directory exists
                                    os.makedirs("output", exist_ok=True)
                                    filename = f"output/task_{i}_output_{file_count}.png"
                                    try:
                                        project_client.agents.files.save(file_id=file_id, file_name=filename)
                                        print(f"Downloaded: {filename}")
                                    except Exception as e:
                                        print(f"Failed to download {filename}: {e}")

            # To review the code interpreter outputs, you can access
            # them from the response raw_representations, just uncomment the next line:
            # print_code_interpreter_inputs(response)


if __name__ == "__main__":
    asyncio.run(main())