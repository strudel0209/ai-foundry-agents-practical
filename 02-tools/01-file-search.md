# 1. File Search Tool - Vector-Based Document Intelligence

In this lesson, you'll master the File Search tool. This tool enables semantic search across your documents using vector embeddings.

## 🎯 Objectives

- Understand vector-based document search concepts
- Upload and index documents for search
- Create agents with File Search capabilities
- Build document processing workflows
- Implement enterprise document intelligence patterns

## 🧠 Key Concepts

### What is File Search?

File Search is a Retrieval-Augmented Generation (RAG) tool in Azure AI Foundry Agent Service that:
- **Indexes documents** using vector embeddings for semantic search
- **Chunks content** into manageable segments for efficient retrieval
- **Ranks results** by semantic relevance and provides citations
- **Supports multiple formats** (PDF, TXT, DOCX, etc.)
- **Integrates with agents and threads** for context-aware responses

### How Does File Search Work in Azure AI Foundry?

- **Upload Documents:** Files are uploaded and stored in either Microsoft-managed storage (basic setup) or your own Azure Blob Storage (standard setup).
- **Vector Store Creation:** Uploaded files are parsed, chunked, and embedded into a vector store, which is a cloud-managed semantic index.
- **Agent Integration:** Agents are configured with the File Search tool, referencing the vector store for document intelligence.
- **Semantic Search:** When a user asks a question, the agent uses the File Search tool to retrieve relevant document chunks, cite sources, and synthesize answers.

### Why Use File Search?

- **Enterprise Knowledge Retrieval:** Augment agent responses with proprietary or business documents.
- **Semantic Understanding:** Go beyond keyword search to find contextually relevant information.
- **Citations and Compliance:** Always cite document sources for transparency and auditability.
- **Scalability:** Vector stores can hold thousands of files and are managed for performance and security.

## 🚀 What Does the Demo Code Do?

The code in `exercises/exercise_1_file_search.py` demonstrates the full workflow for document intelligence with Azure AI Foundry agents:

1. **Creates Sample Documents:** Generates example files (policy, technical manual, contract) for testing.
2. **Uploads Documents:** Uses the SDK to upload files and track them for later cleanup.
3. **Creates or Reuses a Vector Store:** Checks for an existing vector store with the same files, or creates a new one if needed.
4. **Configures an Agent with File Search:** Sets up an agent with instructions and attaches the File Search tool, referencing the vector store.
5. **Executes Search Queries:** For each test query, creates a thread, sends the user question, and runs the agent to retrieve answers.
6. **Displays Results and Citations:** Shows the agent's response and any document citations, demonstrating how the agent grounds its answers in the uploaded files.
7. **(Optional) Cleans Up Resources:** Tracks uploaded files and agents for cleanup, ensuring efficient resource management.

## 💡 File Search Tool Features in Azure AI Foundry

- **Automatic Query Optimization:** User queries are rewritten for optimal retrieval.
- **Parallel Search:** Complex queries are broken down and run in parallel across vector stores.
- **Hybrid Search:** Combines keyword and semantic search for best results.
- **Citation Tracking:** Every answer includes references to the source document chunks.
- **Chunking and Embedding:** Default chunk size is 800 tokens, overlap is 400 tokens, using high-dimensional embeddings.
- **Scalable Storage:** Vector stores can hold up to 10,000 files, with a max file size of 512 MB.

## 🔍 Best Practices

- **Organize Vector Stores:** Separate stores for different document types or business domains.
- **Monitor Vector Store Readiness:** Ensure files are fully processed before running searches.
- **Optimize Queries:** Use clear, specific questions for best semantic results.
- **Audit and Compliance:** Use citations for traceability and regulatory requirements.
- **Resource Management:** Clean up unused agents, files, and vector stores to avoid hitting quotas.

## 🔧 Troubleshooting

- **File Upload Issues:** Check file size and format; ensure authentication and permissions.
- **Search Quality:** Review document content and query phrasing; optimize chunk size if needed.
- **Performance:** Large documents may take time to index; monitor progress and batch uploads for efficiency.

## 📖 Additional Resources

- [Azure AI Foundry Agent Service File Search Tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/file-search)
- [Quickstart: Get started with Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code#add-files-to-the-agent)
- [SDK Reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [2025 Azure AI Foundry Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/)

---

**Ready to try?**  
Run `python exercises/exercise_1_file_search.py` to see document intelligence in action with Azure AI Foundry agents.
