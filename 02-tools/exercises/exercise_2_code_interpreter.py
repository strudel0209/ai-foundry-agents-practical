#!/usr/bin/env python3

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

    # def cleanup(self):
    #     """Clean up resources"""
    #     if self.agent:
    #         self.client.agents.delete_agent(self.agent.id)
    #         print(f"Deleted agent: {self.agent.id}")


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
        
        for i, task in enumerate(tasks, 1):
            print(f"\n--- Task {i}: {task['name']} ---")
            
            result = analyst.analyze_data(task['description'])
            
            # Display text response
            print("Analysis:")
            print(result['text_response'][:500] + "..." if len(result['text_response']) > 500 else result['text_response'])
            
            # Download any generated files
            if result['files']:
                print(f"\nGenerated {len(result['files'])} files:")
                for j, file_info in enumerate(result['files']):
                    filename = f"task_{i}_output_{j+1}.png"
                    if analyst.download_file(file_info['file_id'], filename):
                        print(f"  - {filename}")
        
        print("\n✅ Data analysis demo completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    # finally:
    #     analyst.cleanup()


if __name__ == "__main__":
    run_data_analysis_demo()
