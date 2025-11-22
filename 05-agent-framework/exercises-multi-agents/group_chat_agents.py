# Copyright (c) Microsoft. All rights reserved.

import asyncio
import logging
import os   

from agent_framework import (
    ChatAgent, 
    GroupChatBuilder, 
    GroupChatStateSnapshot, 
    WorkflowOutputEvent, 
    AgentRunEvent,
    AgentRunUpdateEvent,
    AgentRunResponseUpdate
)
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.WARNING)  # Reduce noise

"""
Sample: Group Chat with Simple Speaker Selector Function

What it does:
- Demonstrates the select_speakers() API for GroupChat orchestration
- Uses a pure Python function to control speaker selection based on conversation state
- Alternates between researcher and writer agents in a simple round-robin pattern
- Shows how to access conversation history, round index, and participant metadata

Key pattern:
    def select_next_speaker(state: GroupChatStateSnapshot) -> str | None:
        # state contains: task, participants, conversation, history, round_index
        # Return participant name to continue, or None to finish
        ...

Prerequisites:
- OpenAI environment variables configured for OpenAIChatClient
"""


def select_next_speaker(state: GroupChatStateSnapshot) -> str | None:
    """Simple speaker selector that alternates between researcher and writer.

    This function demonstrates the core pattern:
    1. Examine the current state of the group chat
    2. Decide who should speak next
    3. Return participant name or None to finish

    Args:
        state: Immutable snapshot containing:
            - task: ChatMessage - original user task
            - participants: dict[str, str] - participant names → descriptions
            - conversation: tuple[ChatMessage, ...] - full conversation history
            - history: tuple[GroupChatTurn, ...] - turn-by-turn with speaker attribution
            - round_index: int - number of selection rounds so far
            - pending_agent: str | None - currently active agent (if any)

    Returns:
        Name of next speaker, or None to finish the conversation
    """
    round_idx = state["round_index"]
    history = state["history"]
    
    # Debug: print the selection state
    print(f"\n🎯 [Speaker Selection Round {round_idx}]")
    if history:
        print(f"   Last speaker: {history[-1].speaker}")
    else:
        print(f"   First selection - starting conversation")

    # Finish after 4 rounds (researcher → writer → researcher → writer)
    if round_idx >= 4:
        print("   ✓ Reached maximum rounds - finishing conversation")
        return None

    # Get the last speaker from history
    last_speaker = history[-1].speaker if history else None

    # Simple alternation: researcher → writer → researcher → writer
    if last_speaker == "Researcher":
        next_speaker = "Writer"
    else:
        next_speaker = "Researcher"
    
    print(f"   → Selecting: {next_speaker}")
    return next_speaker


async def main() -> None:
    # Create Azure OpenAI client
    client = AzureOpenAIChatClient(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    
    researcher = ChatAgent(
        name="Researcher",
        description="Collects relevant background information.",
        instructions="""You are a research specialist. Your job is to:
        1. Gather key facts and technical details about the topic
        2. Be concise but thorough
        3. Focus on practical benefits and real-world applications
        Keep your response under 150 words.""",
        chat_client=client
    )

    writer = ChatAgent(
        name="Writer",
        description="Synthesizes a polished answer using the gathered notes.",
        instructions="""You are a technical writer. Your job is to:
        1. Build upon the researcher's findings
        2. Create a clear, well-structured response
        3. Add practical examples if relevant
        4. Summarize key takeaways
        Keep your response under 150 words.""",
        chat_client=client
    )

    # Two ways to specify participants:
    # 1. List form - uses agent.name attribute: .participants([researcher, writer])
    # 2. Dict form - explicit names: .participants(researcher=researcher, writer=writer)
    workflow = (
        GroupChatBuilder()
        .select_speakers(select_next_speaker, display_name="Orchestrator")
        .participants([researcher, writer])  # Uses agent.name for participant names
        .build()
    )

    task = "What are the key benefits of using async/await in Python?"

    print("\n" + "="*80)
    print("🚀 STARTING GROUP CHAT WITH SPEAKER SELECTOR")
    print("="*80)
    print(f"\n📋 TASK: {task}")
    print("="*80)

    # Track all agent responses
    agent_responses = []
    streaming_buffer = []  # Buffer to collect streaming updates
    current_agent = None
    seen_events = set()  # Track unique event types we've seen
    executor_invoked_count = 0  # Track executor invocations
    
    async for event in workflow.run_stream(task):
        event_type = event.__class__.__name__
        
        # Log new event types once for debugging
        if event_type not in seen_events:
            seen_events.add(event_type)
            if event_type not in ['StreamingChunk', 'StreamUpdate', 'AgentRunUpdateEvent', 'AgentRunResponseUpdate']:
                print(f"\n[DEBUG] New event type detected: {event_type}")
        
        # Track ExecutorInvokedEvent to determine which agent is speaking
        if 'ExecutorInvoked' in event_type:
            executor_invoked_count += 1
            
            # The first two ExecutorInvoked events are for each speaker selection
            # Map them to our selected speakers list
            if executor_invoked_count % 2 == 1:  # First of a pair
                # This is the speaker selector executor
                pass
            else:  # Second of a pair
                # This is the actual agent executor
                # Determine which agent based on the selection order
                agent_index = (executor_invoked_count // 2) - 1
                if agent_index == 0:
                    current_agent = "Researcher"  # First selection is always Researcher
                elif agent_index >= 0:
                    # Alternate between Researcher and Writer
                    current_agent = "Writer" if agent_index % 2 == 1 else "Researcher"
                
                # Clear buffer for new agent
                streaming_buffer = []
                if current_agent:
                    print(f"\n🗣️ [{current_agent}] is speaking...")
        
        # Capture streaming updates (text as it's being generated)
        elif isinstance(event, AgentRunUpdateEvent):
            if event.data:
                # Extract text from AgentRunResponseUpdate object
                update_text = ""
                if isinstance(event.data, AgentRunResponseUpdate):
                    # AgentRunResponseUpdate has a text property
                    update_text = event.data.text if hasattr(event.data, 'text') else str(event.data)
                elif isinstance(event.data, str):
                    update_text = event.data
                else:
                    # Try to extract text from other formats
                    update_text = str(event.data)
                
                if update_text:
                    print(update_text, end="", flush=True)
                    streaming_buffer.append(update_text)
            
        # When executor completes, save the buffered response
        elif 'ExecutorCompleted' in event_type:
            if streaming_buffer and current_agent and current_agent not in ["user", "Orchestrator", None]:
                full_text = ''.join(streaming_buffer)
                agent_responses.append({
                    "agent": current_agent,
                    "text": full_text.strip()
                })
                print(f"\n✅ [{current_agent}] Response captured ({len(full_text)} chars)")
                streaming_buffer = []
                # Reset current_agent after capturing
                current_agent = None
                
        # Show final orchestrator message
        elif isinstance(event, WorkflowOutputEvent):
            final_message = event.data
            author = getattr(final_message, "author_name", "Orchestrator")
            text = getattr(final_message, "text", str(final_message))
            
            print(f"\n\n✅ FINAL OUTPUT")
            print("="*80)
            print(f"[{author}]")
            print(text)
            print("="*80)

    # Summary
    print("\n📊 CONVERSATION SUMMARY:")
    print("-"*40)
    if agent_responses:
        for i, response in enumerate(agent_responses, 1):
            print(f"\n{i}. 💬 {response['agent']} spoke:")
            # Show first 200 chars of each response
            preview = response['text'][:200] + "..." if len(response['text']) > 200 else response['text']
            # Clean up preview - remove extra whitespace
            preview = ' '.join(preview.split())
            print(f"   \"{preview[:150]}...\"" if len(preview) > 150 else f"   \"{preview}\"")
    else:
        print("❌ No agent responses were captured")
        print(f"\nDEBUG Info:")
        print(f"  - Event types seen: {len(seen_events)}")
        print(f"  - ExecutorInvoked events: {executor_invoked_count}")
        print(f"  - Expected agent turns: {executor_invoked_count // 2}")
    
    print(f"\n📈 Statistics:")
    print(f"  - Total turns: {len(agent_responses)}")
    print(f"  - Total ExecutorInvoked events: {executor_invoked_count}")
    
    # Show which agents participated
    if agent_responses:
        agents_participated = list(set(r['agent'] for r in agent_responses))
        print(f"  - Agents that participated: {', '.join(agents_participated)}")
        
        # Count responses per agent
        agent_counts = {}
        for r in agent_responses:
            agent_counts[r['agent']] = agent_counts.get(r['agent'], 0) + 1
        
        print(f"  - Responses per agent:")
        for agent, count in agent_counts.items():
            print(f"      • {agent}: {count} response(s)")
    
    print("\n✨ Workflow completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())