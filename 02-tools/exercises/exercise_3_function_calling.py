#!/usr/bin/env python3

import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool


#1st user function - get_current_datetime
def get_current_datetime():
    """Get current date and time"""
    return datetime.now(timezone.utc).isoformat()

#2nd user function - calculate_mortgage
def calculate_mortgage(principal: float, rate: float, years: int):
    """
    Calculate monthly mortgage payment
    
    Args:
        principal: Loan amount in dollars
        rate: Annual interest rate as percentage
        years: Loan term in years
    
    Returns:
        dict: Payment details
    """
    monthly_rate = rate / 100 / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    total_payment = monthly_payment * num_payments
    total_interest = total_payment - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "principal": principal,
        "rate": rate,
        "years": years
    }

#3rd user function - validate_email
def validate_email(email: str):
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        dict: Validation result
    """
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    
    return {
        "email": email,
        "is_valid": is_valid,
        "message": "Valid email format" if is_valid else "Invalid email format"
    }

#4th user function - convert_temperature
def convert_temperature(temperature: float, from_unit: str, to_unit: str):
    """
    Convert temperature between units
    
    Args:
        temperature: Temperature value
        from_unit: Source unit (C, F, K)
        to_unit: Target unit (C, F, K)
        
    Returns:
        dict: Conversion result
    """
    # Convert to Celsius first
    if from_unit.upper() == 'F':
        celsius = (temperature - 32) * 5/9
    elif from_unit.upper() == 'K':
        celsius = temperature - 273.15
    else:
        celsius = temperature
    
    # Convert from Celsius to target unit
    if to_unit.upper() == 'F':
        result = celsius * 9/5 + 32
    elif to_unit.upper() == 'K':
        result = celsius + 273.15
    else:
        result = celsius
    
    return {
        "original_temperature": temperature,
        "original_unit": from_unit.upper(),
        "converted_temperature": round(result, 2),
        "converted_unit": to_unit.upper()
    }


class BusinessLogicAgent:
    def __init__(self):
        load_dotenv()
        self.client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=DefaultAzureCredential(),
            api_version="2025-05-15-preview"
        )
        self.agent = None

    def create_function_agent(self):
        """Create agent with custom function capabilities"""
        agent_name = "business-logic-agent"
        
        # Check if agent already exists
        try:
            existing_agents = self.client.agents.list_agents()
            for agent in existing_agents:
                if agent.name == agent_name:
                    print(f"Using existing agent: {agent.id}")
                    self.agent = agent
                    return self.agent
        except Exception as e:
            print(f"Error checking existing agents: {e}")
        
        # Create new agent if none exists
        user_functions = {
            get_current_datetime,
            calculate_mortgage,
            validate_email,
            convert_temperature
        }
        
        function_tool = FunctionTool(functions=user_functions)
        
        self.agent = self.client.agents.create_agent(
            model=os.getenv('MODEL_DEPLOYMENT_NAME'),
            name=agent_name,
            instructions="""
You are a helpful business assistant with access to utility functions.

Available functions:
- get_current_datetime: Get current date and time
- calculate_mortgage: Calculate mortgage payments
- validate_email: Check email format validity
- convert_temperature: Convert between temperature units

When users ask for calculations or validations:
1. Use the appropriate function
2. Explain the results clearly
3. Provide additional context when helpful
4. Show your work for calculations
""",
            tools=function_tool.definitions
        )
        
        print(f"Created function agent: {self.agent.id}")
        return self.agent

    def process_request(self, request):
        """Process user request with function calling"""
        thread = self.client.agents.threads.create()
        
        # Send user message
        self.client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=request
        )
        
        # Create run and handle function calls
        run = self.client.agents.runs.create(
            thread_id=thread.id,
            agent_id=self.agent.id
        )
        
        # Poll for completion and handle tool calls
        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"Calling function: {function_name}")
                    print(f"Arguments: {function_args}")
                    
                    # Execute the function
                    if function_name == "get_current_datetime":
                        output = get_current_datetime()
                    elif function_name == "calculate_mortgage":
                        output = calculate_mortgage(**function_args)
                    elif function_name == "validate_email":
                        output = validate_email(**function_args)
                    elif function_name == "convert_temperature":
                        output = convert_temperature(**function_args)
                    else:
                        output = f"Unknown function: {function_name}"
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output) if isinstance(output, dict) else str(output)
                    })
                
                # Submit tool outputs
                self.client.agents.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            
            # Update run status
            run = self.client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        
        # Get final response
        if run.status == "completed":
            try:
                messages = self.client.agents.messages.list(thread_id=thread.id)
                
                # Find the agent's last text message
                agent_response = None
                for msg in messages:
                    if msg.role == "assistant" and msg.text_messages:
                        agent_response = msg.text_messages[-1].text.value
                        break
                
                return agent_response if agent_response else "No response from agent"
            except Exception as e:
                print(f"Error retrieving agent response: {e}")
                return "Error retrieving agent response"

    # def cleanup(self):
    #     """Clean up resources"""
    #     if self.agent:
    #         self.client.agents.delete_agent(self.agent.id)
    #         print(f"Deleted agent: {self.agent.id}")


def run_function_calling_demo():
    """Demonstrate function calling capabilities"""
    print("🔧 Starting Function Calling Demo")
    print("=" * 40)
    
    agent = BusinessLogicAgent()
    
    try:
        agent.create_function_agent()
        
        # Test requests
        test_requests = [
            "What's the current date and time?",
            "Calculate the monthly payment for a $350,000 mortgage at 6.5% interest for 30 years",
            "Is 'user@example.com' a valid email address?",
            "Convert 25 degrees Celsius to Fahrenheit",
            "Help me with a $500,000 mortgage at 7% for 15 years, and tell me what time it is",
            "Check if 'invalid-email' is valid and convert 0°C to Kelvin"
        ]
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n--- Request {i} ---")
            print(f"User: {request}")
            
            response = agent.process_request(request)
            print(f"Agent: {response}")
        
        print("\n✅ Function calling demo completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    # finally:
    #     agent.cleanup()


if __name__ == "__main__":
    run_function_calling_demo()
