# Copyright (c) Microsoft. All rights reserved.

import asyncio
import base64
import os
import urllib.request

from agent_framework import ChatMessage, DataContent, Role, TextContent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
load_dotenv()


def create_sample_image() -> str:
    """Download a sample image from Microsoft docs for testing."""
    # Use a real image from Microsoft docs (Seattle skyline) to ensure the model has something to describe
    url = "https://raw.githubusercontent.com/MicrosoftDocs/azure-ai-docs/main/articles/ai-foundry/openai/media/how-to/generated-seattle.png"
    print(f"Downloading sample image from {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            image_content = response.read()
        image_data = base64.b64encode(image_content).decode("utf-8")
        return f"data:image/png;base64,{image_data}"
    except Exception as e:
        print(f"Failed to download sample image: {e}")
        # Fallback to a larger simple red square (100x100) if download fails
        fallback_png = "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuMjWx0aW9AAAAOklEQVR42u3BAQ0AAADCoPdPbQ43oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/BvpAAAG131yYAAAAAElFTkSuQmCC"
        return f"data:image/png;base64,{fallback_png}"


async def test_image() -> None:
    """Test image analysis with Azure OpenAI."""
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option. Requires AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
    # environment variables to be set.
    
    # Remove conflicting API key from environment to force AzureCliCredential usage
    if "AZURE_OPENAI_API_KEY" in os.environ:
        del os.environ["AZURE_OPENAI_API_KEY"]

    # Explicitly configure client to use the correct endpoint from the project resource
    client = AzureOpenAIChatClient(
        credential=AzureCliCredential(),
        endpoint="https://cog-tb7tpjtuee4ji.openai.azure.com/",
        deployment_name="gpt-4.1-mini",
        api_version="2025-04-01-preview"
    )

    image_uri = create_sample_image()

    # Save the generated image to disk so it can be visualized/verified
    try:
        # Extract the base64 part of the data URI
        image_data = base64.b64decode(image_uri.split(",")[1])
        output_path = "generated_sample.png"
        with open(output_path, "wb") as f:
            f.write(image_data)
        print(f"Sample image saved to: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Warning: Could not save sample image: {e}")

    message = ChatMessage(
        role=Role.USER,
        contents=[TextContent(text="What's in this image?"), DataContent(uri=image_uri, media_type="image/png")],
    )

    response = await client.get_response(message)
    print(f"Image Response: {response}")


async def main() -> None:
    print("=== Testing Azure OpenAI Multimodal ===")
    print("Testing image analysis (supported by Chat Completions API)")
    await test_image()


if __name__ == "__main__":
    asyncio.run(main())