# LangDB ADK - Agent Development Kit for LangDB

A comprehensive Google ADK (Agent Development Kit) integration package for LangDB. This package provides seamless integration of LangDB's LLM capabilities, enhanced agent functionality, and distributed tracing into the Google ADK framework.

## Features

- **LangDBLlm**: Native integration with Google ADK's `BaseLlm` interface
- **LangDBAgent**: Enhanced agent class with automatic LangDB callbacks and session management
- **LangDBTracing**: Distributed tracing integration with OpenTelemetry
- Session tracking and thread management across agent invocations
- Comprehensive callback system for model, agent, and tool interactions

## Installation

```bash
pip install langdb_adk
```

## Usage with Google ADK

### Basic Usage with LangDBAgent

```python
import os
import asyncio
from langdb_adk import LangDBLlm, LangDBAgent, LangDBTracing
from google.adk.runners import InMemoryRunner

# Initialize tracing (optional but recommended)
LangDBTracing(collector_endpoint="https://api.staging.langdb.ai:4317")

async def main():
    # Create a LangDB agent with automatic callbacks and session management
    agent = LangDBAgent(
        model=LangDBLlm(model="openai/gpt-4.1"),
        name="my_agent",
        description="A simple agent with LangDB integration",
        instruction="You are a helpful assistant."
    )
    
    # Create a runner to execute the agent
    runner = InMemoryRunner()
    
    # Run the agent with a prompt
    response = await runner.run(agent, "Hello, how are you?")
    print(response.text)

if __name__ == "__main__":
    asyncio.run(main())
```

### Basic Usage with Standard Agent (Legacy)

```python
from langdb_adk import LangDBLlm, LangDBAgent
from langdb_adk import LangDBTracing
LangDBTracing()


root_agent = LangDBAgent(
    model=LangDBLlm(model="openai/gpt-4.1"),
    name="root_agent",
    description="A Travel Conceirge using the services of multiple sub-agents",
    instruction="You are a travel concierge that coordinates with specialist agents.",
)
```

### Complete Example with Sub-Agents and Tracing

```python
from langdb_adk import LangDBLlm, LangDBAgent, LangDBTracing

# Initialize tracing with LangDB collector
LangDBTracing()

# Create sub-agents for different capabilities
planning_agent = LangDBAgent(
    model=LangDBLlm(model="openai/gpt-4.1"),
    name="planning_agent",
    description="Handles travel planning tasks",
    instruction="You help users plan their travel itineraries."
)

booking_agent = LangDBAgent(
    model=LangDBLlm(model="openai/gpt-4.1"),
    name="booking_agent", 
    description="Handles travel booking tasks",
    instruction="You help users book flights, hotels, and activities."
)

# Create main agent with sub-agents
root_agent = LangDBAgent(
    model=LangDBLlm(model="openai/gpt-4.1"),
    name="root_agent",
    description="A Travel Concierge using multiple sub-agents",
    instruction="You are a travel concierge that coordinates with specialist agents.",
    sub_agents=[planning_agent, booking_agent]
)
```

### With MCP Servers

```python
# Configure MCP servers for LangDB
mcp_servers = [
    {
        "server_url": "server_url",
        "type": "sse",
        "name": "search",
        "description": "Web search capabilities via DuckDuckGo"
    }
]


    # Initialize the LangDB LLM with MCP servers
llm = LangDBLlm(
        model="anthropic/claude-sonnet-4",
        api_key=os.getenv("LANGDB_API_KEY"),
        project_id=os.getenv("LANGDB_PROJECT_ID"),
        mcp_servers=mcp_servers
    )
    
    # Create a LangDB agent with MCP capabilities
root_agent = LangDBAgent(
        model=llm,
        name="search_agent",
        description="Agent with web search capabilities")
```

## Configuration

### Environment Variables

- `LANGDB_API_KEY`: Your LangDB API key (required)
- `LANGDB_PROJECT_ID`: Your LangDB project ID (required)
- `LANGDB_TRACING_BASE_URL`: Custom tracing collector endpoint (optional, defaults to `https://api.us-east-1.langdb.ai:4317`)

### LangDBLlm Parameters

- `model`: The name of the model to use (e.g., "anthropic/claude-sonnet-4", "openai/gpt-4.1")
- `api_key`: Your LangDB API key (defaults to `LANGDB_API_KEY` env var)
- `project_id`: Your LangDB project ID (defaults to `LANGDB_PROJECT_ID` env var)
- `extra_headers`: Additional headers to include in requests
- `mcp_servers`: List of MCP server configurations for extended capabilities


### LangDBTracing Parameters

- `collector_endpoint`: OpenTelemetry collector endpoint (defaults to `LANGDB_TRACING_BASE_URL` or `https://api.us-east-1.langdb.ai:4317`)
- `api_key`: Your LangDB API key (defaults to `LANGDB_API_KEY` env var)
- `project_id`: Your LangDB project ID (defaults to `LANGDB_PROJECT_ID` env var)
- `client_name`: Client identifier for tracing (defaults to "adk" for `LangDBAdkTracing`)

## Advanced Features

### Session Management

LangDBAgent automatically manages session tracking across agent invocations:

- **Thread ID**: Maintains consistent session IDs across agent calls within the same conversation
- **Invocation Tracking**: Tracks sequence of invocations for debugging and analytics
- **State Persistence**: Maintains state across callbacks and sub-agent interactions

### Distributed Tracing

LangDBTracing provides comprehensive observability through OpenTelemetry:

- **Automatic Span Creation**: Traces all agent, model, and tool interactions
- **Attribute Mapping**: Maps ADK attributes to LangDB-specific attributes
- **Session Correlation**: Links spans across different agents using consistent thread IDs
- **Run ID Tracking**: Provides unique run identifiers for each execution


#### Custom Tracing Setup

```python
from langdb_adk import LangDBTracing

# Use default endpoints and credentials from environment
tracing = LangDBTracing()

# Or configure custom settings
tracing = LangDBTracing(
    collector_endpoint="https://custom-collector.example.com:4317",
    api_key="your-api-key",
    project_id="your-project-id",
    client_name="adk"
)
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Google ADK Team for the Agent Development Kit
- OpenTelemetry community for distributed tracing standards
