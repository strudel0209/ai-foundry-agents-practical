# 2. Code Interpreter Tool - AI-Powered Data Analysis

In this lesson, you'll master the Code Interpreter tool—a capability that enables Azure AI Foundry agents to write, execute, and iterate on Python code in real-time. This tool is ideal for data analysis, visualization, and computational tasks.

## 🎯 Objectives

- Understand Code Interpreter capabilities and use cases
- Create agents that can execute Python code dynamically
- Build data analysis and visualization workflows
- Implement statistical analysis and reporting systems
- Handle file generation and downloads from agent outputs

## 🧠 Key Concepts

### What is Code Interpreter?

Code Interpreter allows Azure AI agents to:
- **Execute Python code** in a secure sandbox environment
- **Generate visualizations** (charts, plots) using libraries like matplotlib and seaborn
- **Perform data analysis** with pandas, numpy, and other data science libraries
- **Create and download files** (charts, reports, datasets)
- **Iterate on code** based on results and feedback, refining outputs as needed

### How Does Code Interpreter Work in Azure AI Foundry?

- **Agent Configuration:** Agents are created with the Code Interpreter tool enabled. This allows them to process user requests that require code execution.
- **Data Workflow:** The agent receives a user prompt describing a data analysis or visualization task. It generates Python code, executes it in a sandbox, and returns results.
- **File Handling:** Agents can generate files (images, CSVs, reports) and make them available for download.
- **Iterative Execution:** If code fails or needs improvement, the agent can refine and rerun code until the desired output is achieved.

### Why Use Code Interpreter?

- **Automated Data Analysis:** Empower agents to analyze datasets, perform calculations, and generate insights without manual coding.
- **Visualization:** Automatically create professional charts and graphs for business reporting.
- **Statistical Analysis:** Run statistical tests, comparisons, and generate summaries.
- **Custom Workflows:** Build agents for financial analysis, marketing metrics, operational dashboards, and more.

## 🚀 What Does the Demo Code Do?

The code in `exercises/exercise_2_code_interpreter.py` demonstrates the full workflow for data analysis with Azure AI Foundry agents:

1. **Agent Creation:** Sets up a data analyst agent with Code Interpreter enabled, using the specified model (e.g., `gpt-4o-mini`).
2. **Task Execution:** Sends various data analysis tasks to the agent, such as sales analysis, statistical summaries, and product comparisons.
3. **Thread and Run Management:** For each task, creates a new thread, sends the user request, and starts a run to process the analysis.
4. **Polling and Results:** Monitors the run status until completion, then retrieves the agent's response and any generated files.
5. **File Download:** Downloads generated charts or reports using the recommended SDK methods.
6. **Error Handling:** Handles failures gracefully, reporting errors and ensuring robust execution.
7. **Resource Management:** Tracks agents and files for cleanup (optional).

## 💡 Code Interpreter Tool Features in Azure AI Foundry

- **Secure Execution:** Python code runs in a sandboxed environment for safety.
- **Library Support:** Pre-installed data science libraries (pandas, numpy, matplotlib, seaborn, etc.).
- **File Generation:** Agents can create and return images, CSVs, PDFs, and more.
- **Session Management:** Each code interpreter session is isolated per thread and agent.
- **Iterative Refinement:** Agents can improve code based on execution results and user feedback.

## 🔍 Best Practices

- **Clear Task Descriptions:** Provide detailed prompts for agents to generate accurate code and outputs.
- **Monitor Run Status:** Always check run status before accessing results.
- **Download Files Safely:** Use the SDK's recommended file download methods.
- **Resource Cleanup:** Delete unused agents and files to manage quotas.
- **Error Handling:** Implement robust error handling for code execution and file operations.

## 🔧 Troubleshooting

- **Code Execution Issues:** Check for syntax errors, unsupported libraries, or data format problems.
- **File Download Problems:** Ensure correct file IDs and permissions; use fallback methods if needed.
- **Performance:** Large datasets or complex analyses may take longer; monitor run progress.

## 📖 Additional Resources

- [Azure AI Foundry Agent Service Code Interpreter](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter)
- [Code Interpreter Samples](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter-samples)
- [SDK Reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [2025 Azure AI Foundry Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/)

---

**Ready to try?**  
Run `python exercises/exercise_2_code_interpreter.py` to see data analysis and visualization in action with Azure AI Foundry agents.

## 🔍 Best Practices

### Code Quality & Documentation

1. **Clear Comments**: Ensure all generated code is well-commented
2. **Error Handling**: Implement robust error handling in analyses
3. **Reproducibility**: Make analyses reproducible with seed values
4. **Version Control**: Track analysis versions and methodologies

### Performance Optimization

1. **Memory Management**: Handle large datasets efficiently
2. **Code Optimization**: Use vectorized operations where possible
3. **Chunking**: Process large datasets in chunks
4. **Caching**: Cache intermediate results for complex analyses

### Visualization Standards

1. **Professional Charts**: Use consistent, professional styling
2. **Accessibility**: Ensure charts are accessible and readable
3. **Interactive Elements**: Add interactivity where beneficial
4. **Export Quality**: Generate high-quality outputs for presentations

### Security & Compliance

1. **Data Privacy**: Handle sensitive data appropriately
2. **Access Control**: Implement proper access controls
3. **Audit Trails**: Log all analysis activities
4. **Compliance**: Ensure analyses meet regulatory requirements

## 🔧 Troubleshooting

### Common Issues

**Code execution fails:**
- Check for syntax errors in generated code
- Verify library availability and versions
- Review memory usage for large datasets
- Validate input data formats

**File generation problems:**
- Ensure proper file paths and permissions
- Check available disk space
- Verify file format compatibility
- Review export settings

**Performance issues:**
- Optimize data loading and processing
- Use appropriate data structures
- Implement efficient algorithms
- Consider data sampling for large datasets

## 📖 Key Takeaways

After completing this lesson, you should understand:

1. **Code Interpreter Capabilities**: How to leverage AI for dynamic code execution
2. **Data Analysis Workflows**: Building comprehensive analysis pipelines
3. **Visualization Creation**: Generating professional charts and reports
4. **Enterprise Integration**: Scaling code interpreter for business use
5. **Best Practices**: Ensuring quality, security, and performance

## ➡️ Next Step

Once you've mastered Code Interpreter, proceed to [Function Calling](./03-function-calling.md) to learn how to integrate custom business logic and external APIs.
