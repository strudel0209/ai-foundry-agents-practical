# 3. Function Calling - Custom Business Logic Integration

In this lesson, you'll master Function Calling - the powerful capability that enables Azure AI agents to execute custom business logic and integrate with external systems. This tool transforms agents from simple chatbots into sophisticated business automation systems.

## 🎯 Objectives

- Understand function calling concepts and architecture
- Define and register custom functions
- Build agents with business logic capabilities
- Implement error handling and validation
- Create enterprise-grade function calling patterns

## ⏱️ Estimated Time: 75 minutes

## 🧠 Key Concepts

### What is Function Calling?

Function Calling enables agents to:

- **Execute custom code** based on user requests
- **Integrate with APIs** and external systems
- **Perform calculations** and data processing
- **Validate and transform data** according to business rules
- **Orchestrate workflows** across multiple systems

### Function Calling Architecture

```text
User Query → Agent Analysis → Function Selection → Parameter Extraction
                                      ↓
Function Execution → Result Processing → Response Generation → User
```

### Key Components

1. **Function Definitions**: Python functions with proper docstrings
2. **Function Tool**: Tool that makes functions available to agents
3. **Parameter Extraction**: Automatic parsing of function arguments
4. **Result Processing**: Handling function outputs and errors
5. **Response Integration**: Incorporating results into natural language

## 🚀 Step-by-Step Implementation

### Step 1: Defining Business Functions

```python
# exercises/exercise_3_function_calling.py
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool

def get_current_datetime():
    """Get current date and time in UTC format
    
    Returns:
        str: Current datetime in ISO format
    """
    return datetime.now(timezone.utc).isoformat()

def calculate_mortgage(principal: float, rate: float, years: int):
    """
    Calculate monthly mortgage payment using standard formula
    
    Args:
        principal (float): Loan amount in dollars
        rate (float): Annual interest rate as percentage (e.g., 6.5 for 6.5%)
        years (int): Loan term in years
    
    Returns:
        dict: Comprehensive payment breakdown including:
            - monthly_payment: Monthly payment amount
            - total_payment: Total amount paid over loan term
            - total_interest: Total interest paid
            - principal: Original loan amount
            - rate: Interest rate used
            - years: Loan term
    """
    # Convert annual rate to monthly decimal
    monthly_rate = rate / 100 / 12
    num_payments = years * 12
    
    # Handle zero interest rate case
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        # Standard mortgage payment formula
        monthly_payment = principal * (
            monthly_rate * (1 + monthly_rate)**num_payments
        ) / ((1 + monthly_rate)**num_payments - 1)
    
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

def validate_email(email: str):
    """
    Validate email address format using regex
    
    Args:
        email (str): Email address to validate
        
    Returns:
        dict: Validation result with:
            - email: Original email address
            - is_valid: Boolean validation result
            - message: Human-readable validation message
    """
    import re
    
    # RFC 5322 compliant email regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    
    return {
        "email": email,
        "is_valid": is_valid,
        "message": "Valid email format" if is_valid else "Invalid email format"
    }

def convert_temperature(temperature: float, from_unit: str, to_unit: str):
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin
    
    Args:
        temperature (float): Temperature value to convert
        from_unit (str): Source unit (C, F, K)
        to_unit (str): Target unit (C, F, K)
        
    Returns:
        dict: Conversion result with:
            - original_temperature: Input temperature
            - original_unit: Source unit
            - converted_temperature: Result temperature
            - converted_unit: Target unit
    """
    # Normalize unit inputs
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()
    
    # Convert to Celsius as intermediate step
    if from_unit == 'F':
        celsius = (temperature - 32) * 5/9
    elif from_unit == 'K':
        celsius = temperature - 273.15
    else:  # Assume Celsius
        celsius = temperature
    
    # Convert from Celsius to target unit
    if to_unit == 'F':
        result = celsius * 9/5 + 32
    elif to_unit == 'K':
        result = celsius + 273.15
    else:  # Celsius
        result = celsius
    
    return {
        "original_temperature": temperature,
        "original_unit": from_unit,
        "converted_temperature": round(result, 2),
        "converted_unit": to_unit
    }
```

### Step 2: Building the Function Calling Agent

```python
class BusinessLogicAgent:
    """Enterprise-grade agent with custom business logic capabilities"""
    
    def __init__(self):
        load_dotenv()
        self.client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=DefaultAzureCredential(),
            api_version="latest"
        )
        self.agent = None
        self.function_registry = {}

    def register_functions(self):
        """Register all available business functions"""
        
        # Define the functions to make available to the agent
        self.function_registry = {
            'get_current_datetime': get_current_datetime,
            'calculate_mortgage': calculate_mortgage,
            'validate_email': validate_email,
            'convert_temperature': convert_temperature
        }
        
        print(f"📝 Registered {len(self.function_registry)} functions")
        return self.function_registry

    def create_function_agent(self):
        """Create agent with comprehensive function calling capabilities"""
        
        # Register functions first
        user_functions = self.register_functions()
        
        # Create function tool with all registered functions
        function_tool = FunctionTool(functions=set(user_functions.values()))
        
        # Create agent with detailed instructions
        self.agent = self.client.agents.create_agent(
            model=os.getenv('MODEL_DEPLOYMENT_NAME'),
            name="business-logic-agent",
            instructions="""
You are an expert business assistant with access to specialized utility functions.
Your role is to help users with calculations, validations, and data processing tasks.

🔧 Available Functions:
- get_current_datetime: Get current date and time in UTC
- calculate_mortgage: Calculate mortgage payments with full breakdown
- validate_email: Verify email address format compliance
- convert_temperature: Convert between Celsius, Fahrenheit, and Kelvin

💡 Best Practices:
1. Always use the appropriate function for calculations
2. Explain your reasoning and methodology
3. Provide context for results and recommendations
4. Show detailed breakdowns for complex calculations
5. Validate inputs and handle edge cases gracefully

🎯 Response Format:
1. Acknowledge the user's request
2. Execute the relevant function(s)
3. Interpret and explain the results
4. Provide actionable insights or recommendations
5. Offer to perform related calculations if helpful

Always be thorough, accurate, and professional in your responses.
""",
            tools=function_tool.definitions
        )
        
        print(f"🤖 Created function agent: {self.agent.id}")
        print(f"⚙️  Enabled {len(function_tool.definitions)} function tools")
        return self.agent

    def execute_function(self, function_name: str, function_args: dict):
        """Execute a registered function with error handling"""
        
        try:
            if function_name not in self.function_registry:
                return f"❌ Unknown function: {function_name}"
            
            function = self.function_registry[function_name]
            result = function(**function_args)
            
            print(f"✅ Executed {function_name} with args: {function_args}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Function execution failed: {str(e)}"
            print(error_msg)
            return {"error": error_msg}

    def process_request(self, request: str):
        """Process user request with comprehensive function calling"""
        
        print(f"\n🔍 Processing request: {request}")
        
        # Create conversation thread
        thread = self.client.agents.threads.create()
        
        # Send user message
        self.client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=request
        )
        
        # Create and monitor run
        run = self.client.agents.runs.create(
            thread_id=thread.id,
            agent_id=self.agent.id
        )
        
        # Handle function calls in run loop
        while run.status in ["queued", "in_progress", "requires_action"]:
            
            if run.status == "requires_action":
                print("🔧 Agent is requesting function execution...")
                
                # Process required tool calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"  📞 Calling: {function_name}")
                    print(f"  📋 Args: {function_args}")
                    
                    # Execute the function
                    output = self.execute_function(function_name, function_args)
                    
                    # Prepare output for agent
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output) if isinstance(output, dict) else str(output)
                    })
                
                # Submit tool outputs back to agent
                self.client.agents.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                
                print(f"  ✅ Submitted {len(tool_outputs)} tool outputs")
            
            # Update run status
            run = self.client.agents.runs.get(thread_id=thread.id, run_id=run.id)
        
        # Get final response
        if run.status == "completed":
            messages = self.client.agents.messages.list(thread_id=thread.id)
            response = messages.data[0].content[0].text.value
            
            # Clean up thread
            self.client.agents.threads.delete(thread.id)
            return response
        else:
            return f"❌ Request failed with status: {run.status}"

    def cleanup(self):
        """Clean up agent resources"""
        if self.agent:
            self.client.agents.delete_agent(self.agent.id)
            print(f"🧹 Deleted agent: {self.agent.id}")
```

### Step 3: Advanced Function Calling Patterns

```python
def run_comprehensive_demo():
    """Comprehensive demonstration of function calling capabilities"""
    
    print("🔧 Starting Advanced Function Calling Demo")
    print("=" * 50)
    
    agent = BusinessLogicAgent()
    
    try:
        # Initialize agent
        agent.create_function_agent()
        
        # Comprehensive test scenarios
        test_scenarios = [
            {
                "name": "Basic Information Request",
                "request": "What's the current date and time?",
                "expected_functions": ["get_current_datetime"]
            },
            {
                "name": "Financial Calculation",
                "request": "Calculate the monthly payment for a $350,000 mortgage at 6.5% interest for 30 years",
                "expected_functions": ["calculate_mortgage"]
            },
            {
                "name": "Data Validation",
                "request": "Is 'user@example.com' a valid email address?",
                "expected_functions": ["validate_email"]
            },
            {
                "name": "Unit Conversion",
                "request": "Convert 25 degrees Celsius to Fahrenheit",
                "expected_functions": ["convert_temperature"]
            },
            {
                "name": "Multi-Function Request",
                "request": "Help me with a $500,000 mortgage at 7% for 15 years, and tell me what time it is",
                "expected_functions": ["calculate_mortgage", "get_current_datetime"]
            },
            {
                "name": "Complex Validation & Conversion",
                "request": "Check if 'invalid-email' is valid and convert 0°C to Kelvin",
                "expected_functions": ["validate_email", "convert_temperature"]
            },
            {
                "name": "Business Decision Support",
                "request": "Compare mortgage options: $400k at 6% for 30 years vs $400k at 7% for 15 years",
                "expected_functions": ["calculate_mortgage"]
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"📋 Scenario {i}: {scenario['name']}")
            print(f"🔍 Request: {scenario['request']}")
            print(f"🎯 Expected Functions: {', '.join(scenario['expected_functions'])}")
            print("-" * 60)
            
            # Process request
            response = agent.process_request(scenario['request'])
            
            # Display response
            print(f"🤖 Agent Response:")
            print(f"{response}")
            
            # Brief pause between scenarios
            import time
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print("✅ Function calling demonstration completed!")
        print("📊 All scenarios processed successfully")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always cleanup
        agent.cleanup()
```

### Step 4: Enterprise Function Calling Patterns

```python
class EnterpriseBusinessAgent:
    """Enterprise-grade business agent with advanced function calling"""
    
    def __init__(self):
        self.client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=DefaultAzureCredential()
        )
        self.function_categories = {
            'financial': [calculate_mortgage, calculate_loan_interest, calculate_roi],
            'validation': [validate_email, validate_phone, validate_ssn],
            'conversion': [convert_temperature, convert_currency, convert_units],
            'utility': [get_current_datetime, format_date, calculate_business_days]
        }
    
    def create_specialized_agent(self, category: str):
        """Create agent specialized for specific function category"""
        
        if category not in self.function_categories:
            raise ValueError(f"Unknown category: {category}")
        
        functions = self.function_categories[category]
        function_tool = FunctionTool(functions=set(functions))
        
        instructions = self.get_specialized_instructions(category)
        
        agent = self.client.agents.create_agent(
            model=os.getenv('MODEL_DEPLOYMENT_NAME'),
            name=f"{category}-specialist-agent",
            instructions=instructions,
            tools=function_tool.definitions
        )
        
        return agent
    
    def get_specialized_instructions(self, category: str) -> str:
        """Get specialized instructions for each function category"""
        
        instructions = {
            'financial': """
You are a financial calculation specialist. You help with:
- Mortgage and loan calculations
- Investment return analysis
- Financial planning scenarios
- Risk assessments

Always provide detailed breakdowns and explain financial concepts.
""",
            'validation': """
You are a data validation specialist. You help with:
- Email format validation
- Phone number verification
- Data integrity checks
- Compliance validation

Always explain validation criteria and provide correction suggestions.
""",
            'conversion': """
You are a unit conversion specialist. You help with:
- Temperature conversions
- Currency exchange calculations
- Unit measurements
- Data format transformations

Always show conversion formulas and provide context for results.
""",
            'utility': """
You are a utility function specialist. You help with:
- Date and time operations
- Data formatting
- System information
- General calculations

Always provide accurate, well-formatted results with explanations.
"""
        }
        
        return instructions.get(category, "You are a helpful business assistant.")
    
    def route_request(self, request: str) -> str:
        """Intelligent routing of requests to appropriate specialist"""
        
        # Simple keyword-based routing (enhance with ML for production)
        routing_keywords = {
            'financial': ['mortgage', 'loan', 'payment', 'interest', 'finance', 'money'],
            'validation': ['validate', 'check', 'verify', 'email', 'phone', 'format'],
            'conversion': ['convert', 'temperature', 'currency', 'celsius', 'fahrenheit'],
            'utility': ['time', 'date', 'current', 'now', 'format', 'calculate']
        }
        
        request_lower = request.lower()
        scores = {}
        
        for category, keywords in routing_keywords.items():
            score = sum(1 for keyword in keywords if keyword in request_lower)
            scores[category] = score
        
        # Return category with highest score
        best_category = max(scores, key=scores.get)
        return best_category if scores[best_category] > 0 else 'utility'
```

## 🎯 Exercises

### Exercise A: Custom Business Function Library

Build a comprehensive function library for your domain:

1. **Define 10+ business functions** relevant to your use case
2. **Implement proper error handling** and validation
3. **Create function documentation** with examples
4. **Test edge cases** and error scenarios
5. **Build a function registry** for dynamic loading

### Exercise B: Multi-Agent Function Orchestration

Create a system with multiple specialized agents:

1. **Build specialist agents** for different function categories
2. **Implement intelligent routing** based on request analysis
3. **Create cross-agent workflows** for complex tasks
4. **Add monitoring and logging** for function calls
5. **Test scalability** with concurrent requests

### Exercise C: External API Integration

Integrate with external APIs through function calling:

1. **Wrap REST APIs** as callable functions
2. **Handle authentication** and rate limiting
3. **Implement caching** for API responses
4. **Add retry logic** for failed requests
5. **Create API health monitoring**

## 🔍 Best Practices

### Function Design

1. **Clear Documentation**: Write comprehensive docstrings with examples
2. **Type Hints**: Use proper Python type annotations
3. **Error Handling**: Implement robust error handling and validation
4. **Return Standards**: Use consistent return formats (dict/JSON)
5. **Stateless Design**: Keep functions stateless for better scalability

### Performance Optimization

1. **Caching**: Cache expensive function results
2. **Async Operations**: Use async functions for I/O operations
3. **Resource Management**: Properly handle external resource connections
4. **Timeout Handling**: Set appropriate timeouts for long-running functions
5. **Memory Management**: Avoid memory leaks in long-running functions

### Security Considerations

1. **Input Validation**: Always validate function parameters
2. **Access Control**: Implement function-level access controls
3. **Audit Logging**: Log all function calls for security monitoring
4. **Secret Management**: Use secure credential management
5. **Rate Limiting**: Prevent abuse with rate limiting

## 🔧 Troubleshooting

### Common Issues

**Function not found error:**

- Verify function is properly registered in FunctionTool
- Check function name spelling and case sensitivity
- Ensure function has proper docstring

**Parameter parsing errors:**

- Validate JSON parsing of function arguments
- Check parameter types match function signature
- Review function docstring parameter descriptions

**Function execution failures:**

- Implement proper error handling in functions
- Add logging for debugging function execution
- Check for missing dependencies or imports

**Performance issues:**

- Profile function execution times
- Implement caching for repeated calls
- Consider async patterns for I/O operations

## 📖 Key Takeaways

After completing this lesson, you should understand:

1. **Function Calling Architecture**: How agents execute custom business logic
2. **Function Design Patterns**: Best practices for creating callable functions
3. **Error Handling**: Robust error handling and validation techniques
4. **Enterprise Integration**: Patterns for scaling function calling systems
5. **Performance Optimization**: Techniques for optimizing function execution

## ➡️ Next Step

Once you've mastered Function Calling, you're ready to explore advanced orchestration patterns in [Module 3: Orchestration](../03-orchestration/README.md).

---

**💡 Pro Tip**: Function calling is most powerful when combined with other tools. Use File Search to retrieve information, then apply functions to process that data, creating comprehensive business automation workflows.
