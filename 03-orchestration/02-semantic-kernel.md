# 1. Semantic Kernel Integration - Multi-Agent Orchestration

In this lesson, you'll master the integration of Azure AI Foundry agents with Microsoft Semantic Kernel to create multi-agent orchestration patterns.

## 🎯 Objectives

- Understand Semantic Kernel architecture and capabilities
- Integrate Azure AI agents with Semantic Kernel
- Implement multi-agent orchestration patterns
- Build collaborative agent workflows
- Create enterprise-grade agent coordination systems

## 🧠 Key Concepts

### What is Semantic Kernel?

Semantic Kernel (SK) is Microsoft's open-source SDK for orchestrating AI agents, models, and tools. It enables:
- **Multi-agent orchestration**: Coordinate multiple agents for complex workflows
- **Plugin architecture**: Extend agent capabilities with custom functions and tools
- **Memory management**: Maintain context and history across agent interactions
- **Flexible planning**: Automate task decomposition and execution

### How Does SK Integrate with Azure AI Foundry Agents?

- **Direct Agent Wrapping**: SK can wrap Azure AI Foundry agents as SK agents, allowing seamless orchestration and invocation.
- **Unified Interface**: SK agents expose a standard interface for sending messages, receiving responses, and managing context.
- **Orchestration Patterns**: SK supports sequential, round-robin, hybrid, and hierarchical agent workflows.

## 🚀 What Does the Demo Code Do?

The code in `exercises/exercise_2_semantic_kernel.py` demonstrates modern orchestration patterns using SK and Azure AI Foundry agents:

1. **Agent Wrapping**: Wraps Azure AI Foundry agents as SK agents, preserving their capabilities and instructions.
2. **Sequential Orchestration**: Passes a task through a sequence of specialized agents (research, analysis, writing), with each agent building on the previous output.
3. **Round-Robin Discussion**: Simulates a multi-agent panel, where agents take turns contributing to a shared discussion.
4. **Hybrid Orchestration**: Combines sequential and parallel agent workflows for more complex tasks.
5. **Kernel Setup**: Initializes the SK kernel and connects it to Azure AI Foundry via the Python SDK.
6. **Agent Creation and Reuse**: Efficiently creates or reuses agents, avoiding duplication and optimizing resource usage.
7. **Result Synthesis**: Aggregates and summarizes outputs from multiple agents for final reporting.

## 💡 Semantic Kernel Usage Patterns in the Demo

- **Direct SK Agent Wrappers**: The demo uses a direct wrapper class to expose Azure AI Foundry agents as SK agents, enabling invocation and orchestration without plugin indirection.
- **Async Invocation**: All agent interactions are performed asynchronously, supporting scalable and responsive workflows.
- **Multi-Agent Coordination**: The orchestrator manages multiple agents, routing tasks and synthesizing results according to the chosen pattern.
- **Error Handling**: The code handles run statuses, errors, and edge cases gracefully, reporting issues and ensuring robust execution.
- **Result Export**: Outputs from orchestration runs are saved for further analysis or reporting.

## 🔍 Best Practices

- **Use Direct Wrappers**: Wrap Azure AI Foundry agents as SK agents for seamless orchestration.
- **Design Clear Agent Roles**: Assign specific instructions and expertise to each agent for modular workflows.
- **Monitor Run Status**: Always check agent run status and handle errors or required actions.
- **Optimize Resource Usage**: Reuse agents and threads where possible to avoid unnecessary resource consumption.
- **Aggregate Results**: Synthesize outputs from multiple agents for comprehensive reporting.

## 🔧 Troubleshooting

- **API Usage**: Use the correct Azure AI Foundry SDK methods for threads, messages, and runs.
- **ItemPaged Handling**: Iterate over paged results instead of accessing `.data` directly.
- **Content Structure**: Handle both list and direct content formats in agent responses.
- **Run Statuses**: Monitor for all possible run states, including `requires_action`, `failed`, and `expired`.

## 📖 Additional Resources

- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure AI Foundry Agent Service](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/)
- [SK Agent Orchestration Patterns](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/)
- [2025 Azure AI Foundry Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/)

---

**Ready to try?**  
Run `python 03-orchestration/exercises/exercise_2_semantic_kernel.py` to see multi-agent orchestration in action with Semantic Kernel and Azure AI Foundry agents.
- Define a sequence of specialized agents
- Create a workflow that passes output from one agent to the next
- Each agent adds its expertise to the evolving solution
- Final agent delivers the completed result

**Example Scenario**: Creating a comprehensive market analysis report:
1. Research Specialist gathers relevant data and statistics
2. Analysis Specialist interprets data and identifies patterns
3. Writing Specialist produces a polished final document

#### 2. Round-Robin Discussion

Round-robin discussion enables multiple agents to contribute to a conversation in turns, mimicking a panel discussion.

**Use Case**: Collaborative problem-solving, brainstorming, or multi-perspective analysis.

**Implementation Approach**:
- Initialize a shared conversation context
- Each agent takes turns contributing to the conversation
- All agents have access to the full conversation history
- Process continues for a predetermined number of rounds

**Example Scenario**: Expert panel discussion on a complex topic:
1. Different specialists contribute their perspective in turns
2. Each specialist builds on previous contributions
3. The discussion evolves as multiple viewpoints are considered

#### 3. Concurrent Collaboration

Concurrent collaboration allows multiple agents to work simultaneously on different aspects of a problem.

**Use Case**: Parallel processing of independent sub-tasks or analyzing a problem from multiple angles simultaneously.

**Implementation Approach**:
```python
# Key implementation pattern for concurrent orchestration
async def execute_concurrent_workflow(self, request, agents):
    tasks = []
    for agent in agents:
        tasks.append(asyncio.create_task(agent.invoke(request)))
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    # Synthesize the parallel results
    return await self.synthesize_results(results)
```

**Example Scenario**: Comprehensive product review:
1. Technical Specialist evaluates technical specifications
2. UX Specialist assesses user experience
3. Market Specialist analyzes market positioning
4. Results are synthesized into a comprehensive review

#### 4. Human-in-the-Loop Orchestration

Human-in-the-loop orchestration incorporates human feedback and guidance at critical decision points.

**Use Case**: High-stakes decisions, creative work requiring human judgment, or compliance-critical workflows.

**Implementation Approach**:
```python
# Pattern for human-in-the-loop workflow
async def execute_with_human_oversight(self, request, agent, review_points=None):
    # Initial agent response
    initial_response = await agent.invoke(request)
    
    # Request human review
    human_feedback = await self.request_human_feedback(
        initial_response, 
        prompt="Review this response and provide feedback or approval."
    )
    
    if human_feedback.get("approved", False):
        return initial_response
    else:
        # Refine based on feedback
        refined_request = f"""
        Original request: {request}
        Initial response: {initial_response}
        Human feedback: {human_feedback.get('comments', '')}
        
        Please revise your response based on the human feedback.
        """
        return await agent.invoke(refined_request)
```

**Example Scenario**: Content approval workflow:
1. Writing agent drafts content
2. Human reviewer provides feedback
3. Agent refines based on feedback
4. Final human approval before publication

#### 5. Hierarchical Orchestration

Hierarchical orchestration uses a coordinator agent to manage specialized worker agents.

**Use Case**: Complex workflows requiring dynamic task allocation and coordination.

**Implementation Approach**:
```python
# Pattern for hierarchical orchestration
async def execute_hierarchical_workflow(self, request):
    # Coordinator agent analyzes the request and creates a plan
    plan = await self.coordinator_agent.create_plan(request)
    
    results = {}
    for task in plan.tasks:
        # Select appropriate agent for each task
        agent = self.select_agent_for_task(task)
        # Execute task
        task_result = await agent.invoke(task.instructions)
        results[task.id] = task_result
    
    # Synthesize results according to the plan
    return await self.coordinator_agent.synthesize_results(plan, results)
```

**Example Scenario**: Complex project management:
1. Manager Agent breaks down a project into tasks
2. Specialized agents are assigned specific tasks
3. Manager Agent monitors progress and coordinates
4. Manager Agent synthesizes the final deliverable


## 🔍 Best Practices

### Agent Design Principles

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Clear Instructions**: Provide detailed, specific instructions for each agent
3. **Consistent Interfaces**: Use standardized input/output formats
4. **Error Handling**: Implement robust error handling and recovery
5. **Performance Monitoring**: Track agent performance and optimize

### Orchestration Patterns

1. **Sequential Workflows**: For dependent tasks requiring specific order
2. **Parallel Execution**: For independent tasks that can run concurrently
3. **Conditional Branching**: For workflows with decision points
4. **Loop Patterns**: For iterative processes and refinement
5. **Error Recovery**: For handling failures gracefully

### Performance Optimization

1. **Caching**: Implement response caching to avoid redundant calls
2. **Batching**: Batch related requests where possible
3. **Streaming**: Use streaming for long-running operations
4. **Resource Management**: Implement proper lifecycle management
5. **Load Balancing**: Distribute workload across multiple instances

## 🔧 Troubleshooting

### Common Issues

**Azure AI SDK API errors:**

- Use the correct sub-client structure (e.g., `client.agents.threads.create()`)
- Handle `ItemPaged` objects with iteration, not `.data` attribute
- Check message content structure and handle both list and direct formats
- Monitor run status for all possible states including `requires_action`

**Orchestration failures:**

- Implement proper timeout handling with exponential backoff
- Add comprehensive logging at each workflow stage
- Create visualization tools for workflow execution
- Implement circuit breakers for unreliable services

**Context management issues:**

- Implement context pruning for large conversation histories
- Use selective context retention for important information
- Implement hierarchical context structures
- Monitor token usage across conversation turns

## 📖 Key Takeaways

After completing this lesson, you should understand:

1. **Direct SK-Foundry Integration**: How to wrap Azure AI Foundry agents as SK agents
2. **Orchestration Patterns**: Various patterns for agent collaboration
3. **Implementation Approaches**: Key implementation techniques for each pattern
4. **Best Practices**: Design principles for effective agent orchestration
5. **Troubleshooting**: Common issues and their solutions

## ➡️ Next Step

Once you've mastered Semantic Kernel integration, proceed to [Advanced Orchestration Patterns](./03-advanced-orchestration.md) to learn enterprise-grade multi-agent systems.
