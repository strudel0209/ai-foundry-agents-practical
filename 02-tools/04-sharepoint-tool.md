# 4. SharePoint Tool - Enterprise Document Intelligence

In this lesson, you'll master the SharePoint tool for Azure AI Foundry agents. This tool enables secure access to your organization's SharePoint documents with enterprise-grade authentication and retrieval.

## 🎯 Objectives

- Understand SharePoint integration with Azure AI agents
- Configure SharePoint connections securely
- Create agents with SharePoint document access
- Implement enterprise document retrieval workflows
- Handle authentication and access control

## 🧠 Key Concepts

### What is the SharePoint Tool?

The SharePoint tool is an enterprise integration in Azure AI Foundry Agent Service that:
- **Connects to SharePoint sites** securely using managed identity
- **Leverages Microsoft 365 Copilot API** for intelligent document retrieval
- **Implements On-Behalf-Of (OBO) authentication** for user-specific access
- **Uses built-in indexing** from Microsoft's semantic search capabilities
- **Maintains enterprise security** with document-level access control

### How Does SharePoint Integration Work?

1. **Connection Setup:** A SharePoint connection is created in Azure AI Foundry, linking to your SharePoint site or folder
2. **Identity Passthrough:** Uses the end user's identity to authorize and retrieve documents they have permission to access
3. **Semantic Indexing:** Leverages Microsoft 365 Copilot's built-in indexing for intelligent document chunking and retrieval
4. **Agent Integration:** Agents use the SharePoint tool to query documents based on user questions
5. **Secure Retrieval:** Only documents the user has access to are retrieved and used for generating responses

### Why Use SharePoint Tool?

- **Enterprise Data Access:** Connect AI agents to your organization's knowledge base
- **Security Compliance:** Maintains existing SharePoint permissions and access controls
- **No Data Export Required:** Documents stay in SharePoint, accessed via secure APIs
- **Automatic Updates:** Always uses the latest version of documents without manual synchronization
- **Audit Trail:** Full traceability of which documents were accessed for each query

## 🚀 What Does the Demo Code Do?

The code in `exercises/exercise_4_sharepoint_tool.py` demonstrates the complete workflow for SharePoint integration:

### 1. **Environment Setup**
- Validates required environment variables (`PROJECT_ENDPOINT`, `MODEL_DEPLOYMENT_NAME`, `SHAREPOINT_CONNECTION_NAME`)
- Initializes the Azure AI Project client with default credentials

### 2. **SharePoint Tool Configuration**
- Retrieves the SharePoint connection by name from the project
- Creates a `SharepointTool` instance with the connection ID
- Handles connection errors gracefully with clear error messages

### 3. **Agent Creation**
- Creates an agent with specific instructions for SharePoint document handling
- Attaches the SharePoint tool definitions to enable document search
- Provides detailed prompting to optimize search behavior

### 4. **Query Execution**
- Creates a new thread for each conversation
- Sends user queries about SharePoint documents
- Processes runs and waits for completion
- Displays agent responses with document-based answers

### 5. **Error Handling**
- Validates connection existence before proceeding
- Provides clear error messages for troubleshooting
- Handles run failures gracefully

## 💡 SharePoint Tool Features

### Supported Capabilities
- **Document Types:** `.pdf`, `.docx`, `.ppt`, `.txt`, `.aspx`
- **Site Support:** SharePoint sites and specific folders
- **Search Scope:** All supported documents in the connected site/folder
- **Access Control:** Respects user permissions automatically

### Prerequisites
- **Microsoft 365 Copilot License:** Required for both developers and end users
- **Azure RBAC Role:** At least `Azure AI User` role
- **SharePoint Access:** `READ` permissions on the target site
- **Connection Setup:** SharePoint connection created in Azure AI Foundry

### Connection URL Formats
- **SharePoint Site:** `https://company.sharepoint.com/teams/<site_name>`
- **SharePoint Folder:** `https://company.sharepoint.com/teams/<site_name>/Shared%20documents/<folder_name>`

## 🔍 Best Practices

### Connection Management
- **One Connection Per Site:** Create separate connections for different SharePoint sites
- **Secret Storage:** Always mark SharePoint URLs as secrets in connections
- **Connection Naming:** Use descriptive names for easy identification

### Agent Instructions
- **Be Specific:** Provide clear instructions about document types and search strategies
- **Multiple Attempts:** Configure agents to try different search queries if initial attempts fail
- **File Type Awareness:** Mention expected file types in the instructions

### Query Optimization
- **Clear Questions:** Encourage users to ask specific questions about documents
- **Broad to Specific:** Start with general searches, then narrow down
- **Wildcards:** Use broader terms when specific searches return no results

### Security Considerations
- **License Verification:** Ensure all users have Microsoft 365 Copilot licenses
- **Permission Auditing:** Regularly review SharePoint access permissions
- **Data Governance:** Understand that documents remain in SharePoint, not copied

## 🔧 Troubleshooting

### Common Issues

1. **"Connection not found" Error**
   - Verify connection name matches exactly in Azure portal
   - Ensure connection is created in the same project
   - Check RBAC permissions on the project

2. **"No documents found" Response**
   - Verify Microsoft 365 Copilot license is active
   - Check SharePoint site permissions for the user
   - Ensure documents are indexed (may take time for new files)
   - Try broader search terms or wildcards

3. **Authentication Failures**
   - Run `az login` to refresh credentials
   - Verify Azure AD/Entra ID permissions
   - Check if MFA is required and complete it

4. **SharePoint URL Issues**
   - Use the exact format without query parameters
   - Don't copy the full browser URL
   - Ensure proper URL encoding for spaces (%20)

### Performance Optimization
- **Simple Folder Structure:** Start with sites that have organized content
- **Document Count:** Begin with smaller document sets for testing
- **Query Specificity:** More specific queries return faster results

## 📊 Code Structure Explained

### SharePointDemo Class
- **`__init__`:** Sets up the client and validates environment
- **`setup_sharepoint_tool()`:** Retrieves connection and creates tool instance
- **`create_agent()`:** Configures agent with SharePoint capabilities
- **`run_query()`:** Executes searches and displays results

### Key SDK Methods Used
- **`connections.get()`:** Retrieves SharePoint connection details
- **`SharepointTool()`:** Creates tool instance with connection
- **`agents.create_agent()`:** Creates agent with tool definitions
- **`runs.create_and_process()`:** Executes agent with automatic polling

## 📖 Additional Resources

- [Use the Microsoft SharePoint tool (preview)](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/sharepoint)
- [Microsoft 365 Copilot API Overview](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/api-reference/retrieval-api-overview)
- [SharePoint Tool Samples](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/sharepoint-samples)
- [Azure AI Foundry Agent Service](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/)

---

**Ready to connect?**  
Run `python exercises/exercise_4_sharepoint_tool.py` to integrate SharePoint documents with your Azure AI Foundry agents!

**Note:** Ensure you have created the SharePoint connection in Azure AI Foundry portal before running the exercise.