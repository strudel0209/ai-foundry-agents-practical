# 2. Code Interpreter Tool - AI-Powered Data Analysis

In this lesson, you'll master the Code Interpreter tool - a powerful capability that enables AI agents to write, execute, and iterate on Python code in real-time. This tool is perfect for data analysis, visualization, and computational tasks.

## 🎯 Objectives

- Understand Code Interpreter capabilities and use cases
- Create agents that can execute Python code dynamically
- Build data analysis and visualization workflows
- Implement statistical analysis and reporting systems
- Handle file generation and downloads from agent outputs

## ⏱️ Estimated Time: 75 minutes

## 🧠 Key Concepts

### What is Code Interpreter?

Code Interpreter is a powerful tool that allows AI agents to:
- **Execute Python code** in a secure sandbox environment
- **Generate visualizations** using matplotlib, seaborn, plotly
- **Perform data analysis** with pandas, numpy, scipy
- **Create and download files** (charts, reports, datasets)
- **Iterate on code** based on results and feedback

### Code Execution Architecture

```
User Request → Agent Analysis → Code Generation → Execution → Results → File Output
                    ↓                                       ↓
            Code Refinement ← Error Handling ← Validation ← Response
```

### Key Components

1. **Sandbox Environment**: Secure Python execution context
2. **File System**: Temporary storage for generated files
3. **Library Access**: Pre-installed data science libraries
4. **Output Handling**: Text, images, and downloadable files

## 🚀 Step-by-Step Implementation

### Step 1: Setting Up the Data Analysis Agent

```python
# exercises/exercise_2_code_interpreter.py
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import CodeInterpreterTool

class DataAnalyst:
    def __init__(self):
        load_dotenv()
        self.client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=DefaultAzureCredential(),
            api_version="2025-05-15-preview"
        )
        self.agent = None

    def create_data_agent(self):
        """Get existing agent or create a new one with code interpreter capabilities."""
        agent_name = "data-analyst-agent"
        model_name = os.getenv('MODEL_DEPLOYMENT_NAME')
        code_tool = CodeInterpreterTool()
        
        # Try to find existing agent by name
        try:
            agents = self.client.agents.list_agents()
            for agent in agents:
                if getattr(agent, "name", None) == agent_name:
                    self.agent = agent
                    print(f"Using existing data analyst agent: {self.agent.id}")
                    return self.agent
        except Exception as e:
            print(f"Error listing agents: {e}")
            
        # Create new agent if not found
        self.agent = self.client.agents.create_agent(
            model=model_name,
            name=agent_name,
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
5. Save any charts or outputs as files
""",
            tools=code_tool.definitions,
            tool_resources=code_tool.resources
        )
        
        print(f"Created data analyst agent: {self.agent.id}")
        return self.agent
```

### Step 2: Data Analysis Workflows

```python
def analyze_data(self, task_description):
    """Send analysis task to agent and ensure agent is always associated with the run."""
    if not self.agent:
        raise RuntimeError("Agent is not initialized. Call create_data_agent() first.")
        
    thread = self.client.agents.threads.create()
    
    self.client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=task_description
    )
    
    run = self.client.agents.runs.create(
        thread_id=thread.id,
        agent_id=self.agent.id
    )
    
    # Poll for completion
    import time
    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        run = self.client.agents.runs.get(thread_id=thread.id, run_id=run.id)
    
    if run.status == "completed":
        messages = list(self.client.agents.messages.list(thread_id=thread.id))
        if not messages:
            return {'text_response': 'No response from agent.', 'files': []}
            
        # Find the first assistant message with content
        response_msg = next((m for m in messages if getattr(m, "role", None) == "assistant" and getattr(m, "content", None)), messages[0])
        text_response = ''
        files = []
        
        if hasattr(response_msg, 'content') and response_msg.content:
            # Get the first text chunk
            for content in response_msg.content:
                if hasattr(content, 'text') and content.text:
                    text_response = content.text.value
                    break
                    
            # Check for generated files (image_file or file)
            for content in response_msg.content:
                if hasattr(content, 'image_file') and content.image_file:
                    files.append({
                        'type': 'image',
                        'file_id': content.image_file.file_id
                    })
                elif hasattr(content, 'file') and content.file:
                    files.append({
                        'type': 'file',
                        'file_id': content.file.file_id
                    })
        
        return {
            'text_response': text_response,
            'files': files
        }
    else:
        error_msg = getattr(run, 'last_error', None)
        return {'text_response': f"Analysis failed: {run.status}. {error_msg if error_msg else ''}", 'files': []}

def download_file(self, file_id, filename):
    """Download generated file using the correct Azure AI Foundry SDK method."""
    try:
        # Method 1: Use the save method (recommended)
        agents_client = self.client.agents
        agents_client.files.save(file_id=file_id, file_name=filename)
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Download failed with save method: {e}")
        # Method 2: Alternative approach using get_content
        try:
            agents_client = self.client.agents
            file_content_stream = agents_client.files.get_content(file_id)
            
            with open(filename, "wb") as f:
                for chunk in file_content_stream:
                    if isinstance(chunk, (bytes, bytearray)):
                        f.write(chunk)
                    else:
                        f.write(chunk.encode() if isinstance(chunk, str) else bytes(chunk))
            
            print(f"Downloaded: {filename}")
            return True
        except Exception as e2:
            print(f"Download failed with get_content method: {e2}")
            return False
```

**Important Note**: The file download functionality uses the correct Azure AI agents SDK methods. The `agents_client.files.save()` method is the recommended approach, with `agents_client.files.get_content()` as a fallback option.
```

### Step 3: Advanced Analysis Scenarios

```python
def run_data_analysis_demo():
    """Demonstrate code interpreter capabilities"""
    print("📊 Starting Data Analysis Demo")
    print("=" * 40)
    
    analyst = DataAnalyst()
    
    try:
        analyst.create_data_agent()
        
        # Analysis tasks
        tasks = [
            {
                'name': 'Sales Analysis',
                'description': '''
Analyze sales data and create visualizations:

Create a dataset with daily website visitors for the last 30 days:
- Start with 1000 visitors on day 1
- Add random daily variation (±10%)
- Include a weekly pattern (weekends 20% lower)
- Add a growth trend of 2% per week

Tasks:
1. Generate the synthetic dataset
2. Identify weekly patterns and trends
3. Create comprehensive visualizations
4. Perform seasonal decomposition
5. Forecast next 7 days using simple methods
6. Generate a professional report
''',
            'expected_outputs': ['time_series_chart.png', 'forecast_chart.png', 'analysis_report.txt']
        },
        
        {
            'name': 'A/B Testing Analysis',
            'description': '''
Analyze A/B test results for email campaign performance:

Control Group (A): 2000 emails sent, 180 clicks (9% CTR)
Test Group (B): 2000 emails sent, 220 clicks (11% CTR)

Raw data simulation:
- Control: 1820 no-clicks, 180 clicks
- Test: 1780 no-clicks, 220 clicks

Tasks:
1. Create the dataset with individual user responses
2. Calculate conversion rates and confidence intervals
3. Perform statistical significance testing (chi-square, t-test)
4. Create visualization comparing groups
5. Calculate required sample size for future tests
6. Provide actionable recommendations
''',
            'expected_outputs': ['ab_test_results.png', 'significance_chart.png']
        },
        
        {
            'name': 'Customer Segmentation',
            'description': '''
Perform customer segmentation analysis using RFM analysis:

Generate customer data with:
- 500 customers
- Purchase history (recency, frequency, monetary)
- Realistic distributions and correlations

Customer segments should include:
- Champions (high R, F, M)
- Loyal Customers (high F, M)
- Potential Loyalists (high R, low F)
- At Risk (low R, high F, M)
- Cannot Lose Them (low R, high M)

Tasks:
1. Generate realistic customer purchase data
2. Calculate RFM scores for each customer
3. Perform customer segmentation
4. Create visualizations for each segment
5. Provide marketing strategies for each segment
6. Export customer lists by segment
''',
            'expected_outputs': ['rfm_analysis.png', 'customer_segments.png', 'segment_strategies.txt']
        }
    ]
    
    for task in advanced_tasks:
        print(f"\n🔍 {task['name']}")
        print("=" * 50)
        
        result = analyst.analyze_data(task['description'])
        
        # Display results
        print("📊 Analysis Results:")
        print(result['text_response'][:300] + "..." if len(result['text_response']) > 300 else result['text_response'])
        
        # Download files
        if result['files']:
            print(f"\n📁 Generated Files ({len(result['files'])]):")
            for i, file_info in enumerate(result['files']):
                filename = f"{task['name'].lower().replace(' ', '_')}_output_{i+1}.png"
                if analyst.download_file(file_info['file_id'], filename):
                    print(f"  ✅ {filename}")
        
        print("\n" + "─" * 60)
```

### Step 4: Enterprise Data Analysis Patterns

```python
class EnterpriseDataAnalyst:
    """Enterprise-grade data analysis system with Code Interpreter"""
    
    def __init__(self, project_client):
        self.client = project_client
        self.specialized_agents = {}
        self.analysis_templates = {}
        
    def create_specialized_analysts(self):
        """Create specialized analyst agents for different domains"""
        
        analyst_configs = {
            "financial_analyst": {
                "instructions": """
You are a financial data analyst specializing in:
- Revenue analysis and forecasting
- Cost optimization studies
- ROI calculations and business metrics
- Financial reporting and dashboards

Use professional financial analysis techniques and create
executive-ready visualizations and reports.
""",
                "focus": "financial_metrics"
            },
            
            "marketing_analyst": {
                "instructions": """
You are a marketing data analyst specializing in:
- Campaign performance analysis
- Customer acquisition metrics
- A/B testing and conversion optimization
- Customer lifetime value analysis

Focus on actionable marketing insights and ROI optimization.
""",
                "focus": "marketing_metrics"
            },
            
            "operations_analyst": {
                "instructions": """
You are an operations analyst specializing in:
- Process efficiency analysis
- Quality metrics and control charts
- Capacity planning and resource optimization
- Performance benchmarking

Provide data-driven operational improvements and efficiency gains.
""",
                "focus": "operational_metrics"
            }
        }
        
        for analyst_type, config in analyst_configs.items():
            code_tool = CodeInterpreterTool()
            
            agent = self.client.agents.create_agent(
                model=os.getenv('MODEL_DEPLOYMENT_NAME'),
                name=f"enterprise-{analyst_type}",
                instructions=config["instructions"],
                tools=code_tool.definitions,
                tool_resources=code_tool.resources
            )
            
            self.specialized_agents[analyst_type] = {
                'agent': agent,
                'focus': config['focus']
            }
            
            print(f"✅ Created {analyst_type}: {agent.id}")
    
    def create_analysis_templates(self):
        """Create reusable analysis templates"""
        
        self.analysis_templates = {
            "executive_dashboard": """
Create an executive dashboard with the following components:
1. Key Performance Indicators (KPIs) summary
2. Trend analysis over time
3. Comparative analysis (YoY, QoQ)
4. Risk indicators and alerts
5. Actionable recommendations

Export as both PNG charts and PDF report.
""",
            
            "deep_dive_analysis": """
Perform comprehensive deep-dive analysis:
1. Data quality assessment
2. Exploratory data analysis
3. Statistical testing and validation
4. Predictive modeling (if applicable)
5. Detailed findings and insights
6. Implementation roadmap

Generate detailed technical report with all supporting charts.
""",
            
            "monitoring_report": """
Create automated monitoring report:
1. Current performance vs. targets
2. Anomaly detection and alerts
3. Trend analysis and forecasting
4. Comparative benchmarking
5. Automated insights and recommendations

Format for automated distribution.
"""
        }
    
    def route_analysis_request(self, request: str, data_context: str = None):
        """Intelligently route analysis requests to appropriate specialist"""
        
        # Keywords for routing
        routing_keywords = {
            "financial_analyst": [
                "revenue", "profit", "cost", "roi", "financial", "budget", 
                "expense", "income", "cash flow", "margin"
            ],
            "marketing_analyst": [
                "campaign", "conversion", "ctr", "cac", "ltv", "marketing",
                "customer", "acquisition", "retention", "engagement"
            ],
            "operations_analyst": [
                "efficiency", "process", "quality", "capacity", "performance",
                "operations", "production", "workflow", "optimization"
            ]
        }
        
        request_lower = request.lower()
        scores = {}
        
        for analyst_type, keywords in routing_keywords.items():
            score = sum(2 if keyword in request_lower else 0 for keyword in keywords)
            scores[analyst_type] = score
        
        # Add context-based scoring
        if data_context:
            context_lower = data_context.lower()
            for analyst_type, keywords in routing_keywords.items():
                context_score = sum(1 if keyword in context_lower else 0 for keyword in keywords)
                scores[analyst_type] += context_score
        
        # Return best match or default
        best_analyst = max(scores, key=scores.get) if max(scores.values()) > 0 else "financial_analyst"
        return best_analyst
    
    async def process_enterprise_analysis(self, request: str, template: str = None, data_context: str = None):
        """Process enterprise analysis request with appropriate specialist"""
        
        # Route to appropriate analyst
        analyst_type = self.route_analysis_request(request, data_context)
        agent_info = self.specialized_agents[analyst_type]
        
        print(f"🎯 Routing to: {analyst_type}")
        print(f"🔍 Focus area: {agent_info['focus']}")
        
        # Apply template if specified
        if template and template in self.analysis_templates:
            request = f"{self.analysis_templates[template]}\n\nSpecific Request: {request}"
        
        # Add data context if provided
        if data_context:
            request = f"Data Context: {data_context}\n\n{request}"
        
        # Execute analysis
        thread = self.client.agents.threads.create()
        
        self.client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=request
        )
        
        run = self.client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent_info['agent'].id
        )
        
        if run.status == "completed":
            messages = self.client.agents.messages.list(thread_id=thread.id)
            response = messages.data[0]
            
            result = {
                'analyst_type': analyst_type,
                'text_response': response.content[0].text.value if response.content else '',
                'files': [],
                'recommendations': []
            }
            
            # Extract files and recommendations
            for content in response.content:
                if hasattr(content, 'image_file'):
                    result['files'].append({
                        'type': 'image',
                        'file_id': content.image_file.file_id
                    })
            
            self.client.agents.threads.delete(thread.id)
            return result
        else:
            return {
                'analyst_type': analyst_type,
                'text_response': f"Analysis failed: {run.status}",
                'files': [],
                'recommendations': []
            }
```

## 🎯 Exercises

### Exercise A: Financial Dashboard Creation

Build a comprehensive financial dashboard:

1. Generate sample financial data (revenue, costs, profits)
2. Create interactive visualizations
3. Implement KPI calculations
4. Build executive summary reports
5. Add forecasting capabilities

### Exercise B: Real-Time Data Processing

Implement real-time data analysis:

1. Simulate streaming data sources
2. Create rolling calculations and metrics
3. Implement anomaly detection
4. Build alerting mechanisms
5. Generate automated reports

### Exercise C: Multi-Dataset Analysis

Build a system that analyzes multiple related datasets:

1. Create synthetic business datasets (sales, inventory, customers)
2. Implement cross-dataset analysis
3. Build correlation and causation studies
4. Create comprehensive business insights
5. Generate strategic recommendations

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

## 📊 Advanced Features

### Custom Libraries and Functions

```python
# Example: Creating custom analysis functions
def create_custom_analysis_functions():
    """Create custom functions for specialized analysis"""
    
    custom_functions = """
    def calculate_business_metrics(revenue, costs, customers):
        '''Calculate key business metrics'''
        profit_margin = (revenue - costs) / revenue * 100
        revenue_per_customer = revenue / customers
        cost_per_customer = costs / customers
        
        return {
            'profit_margin': profit_margin,
            'revenue_per_customer': revenue_per_customer,
            'cost_per_customer': cost_per_customer
        }
    
    def create_executive_chart(data, title, filename):
        '''Create executive-style charts'''
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(12, 8))
        # Custom styling for executive presentations
        ax.set_title(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        return filename
    """
    
    return custom_functions
```

### Automated Report Generation

```python
def generate_automated_report(analysis_results):
    """Generate automated analysis reports"""
    
    report_template = """
    # Executive Analysis Report
    
    ## Key Findings
    {key_findings}
    
    ## Detailed Analysis
    {detailed_analysis}
    
    ## Recommendations
    {recommendations}
    
    ## Supporting Charts
    {chart_references}
    
    ## Methodology
    {methodology}
    """
    
    # Process results and generate report
    return report_template.format(**analysis_results)
```

## 📖 Key Takeaways

After completing this lesson, you should understand:

1. **Code Interpreter Capabilities**: How to leverage AI for dynamic code execution
2. **Data Analysis Workflows**: Building comprehensive analysis pipelines
3. **Visualization Creation**: Generating professional charts and reports
4. **Enterprise Integration**: Scaling code interpreter for business use
5. **Best Practices**: Ensuring quality, security, and performance

## ➡️ Next Step

Once you've mastered Code Interpreter, proceed to [Function Calling](./03-function-calling.md) to learn how to integrate custom business logic and external APIs.

---

**💡 Pro Tip**: Code Interpreter is most powerful when combined with domain expertise. Create specialized agents for different business functions to get the most relevant and actionable insights.
