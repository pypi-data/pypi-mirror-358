# Autonomize Observer

A comprehensive SDK for monitoring, tracing, and tracking costs for LLM applications with deep MLflow integration.

## Features

- **Automated LLM Monitoring**: Automatically monitor API calls for clients like OpenAI and Anthropic.
- **End-to-End Agent Tracing**: Trace complex, multi-step agent or flow executions, capturing performance, costs, and data at each step.
- **Centralized Cost Tracking**: Consolidate token usage and costs from multiple LLM calls within a single agent run.
- **Rich MLflow Integration**: Log traces, metrics, parameters, and artifacts to MLflow for powerful experiment tracking and visualization.
- **Async First**: Designed for modern, asynchronous applications.

## Installation

Install the package using pip:

```bash
pip install autonomize-observer
```

### With Provider-Specific Dependencies

```bash
# For OpenAI support
pip install "autonomize-observer[openai]"

# For Anthropic support
pip install "autonomize-observer[anthropic]"

# For both OpenAI and Anthropic
pip install "autonomize-observer[openai,anthropic]"
```

## Core Features

### 1. Automated LLM Monitoring

Wrap your LLM client with `monitor` to automatically track every API call, including performance, token usage, and costs. This is ideal for scenarios where you want detailed logs for each individual LLM interaction.

```python
import os
from openai import OpenAI
from autonomize_observer import monitor

# Set your MLflow tracking URI if not using a local server
# os.environ["MLFLOW_TRACKING_URI"] = "https://your-mlflow-server.com"

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Enable monitoring
# The first argument is the client, and the experiment_name is for MLflow.
monitor(client, experiment_name="Monitored LLM Calls")

# Use the client as normal - every call is now tracked in MLflow
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What is the capital of France?"}]
)
print(response.choices[0].message.content)
```

### 2. End-to-End Agent and Flow Tracing

For complex, multi-step processes, the `MLflowLangflowTracer` captures entire execution flows in a single coherent trace with consolidated metrics.

```python
from autonomize_observer.tracing import MLflowLangflowTracer
from autonomize_observer import monitor

# Initialize tracer for multi-step workflow
tracer = MLflowLangflowTracer(
    trace_name='AI Workflow',
    trace_type='flow',
    project_name='my-project'
)

# Monitor LLM calls within the trace
client = OpenAI()
monitor(client, use_async=False)

# Step 1: Add trace for each component
tracer.add_trace(
    trace_id="step1",
    trace_name="Research Phase", 
    inputs={"query": "research topic"}
)

# Make LLM call (automatically tracked)
response = client.chat.completions.create(...)
tracer.end_trace(trace_id="step1", outputs={"result": response.content})

# Step 2: Continue workflow
tracer.add_trace(trace_id="step2", trace_name="Analysis Phase")
# ... more LLM calls
tracer.end_trace(trace_id="step2", outputs={"analysis": result})

# Complete the workflow
tracer.end(inputs={"workflow": "multi-step"}, outputs={"final": results})
```

**Results in MLflow:**
- Visual trace of execution path with timing
- Consolidated metrics: `total_cost`, `total_tokens`, `duration_ms`
- Component-level breakdowns and I/O data

## Quick Start

### Basic Usage with OpenAI

```python
import os
from openai import OpenAI
from autonomize_observer import monitor

# Set environment variables for authentication
os.environ["MLFLOW_TRACKING_URI"] = "https://your-mlflow-server.com"
# OR use Modelhub credentials:
# os.environ["MODELHUB_URI"] = "https://your-modelhub-url.com"
# os.environ["MODELHUB_AUTH_CLIENT_ID"] = "your-client-id"
# os.environ["MODELHUB_AUTH_CLIENT_SECRET"] = "your-client-secret"
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Create OpenAI client
client = OpenAI()

# Enable monitoring (provider is auto-detected)
monitor(client)

# Use the client as normal - monitoring happens automatically
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ]
)

print(response.choices[0].message.content)
```

### Using with Anthropic

```python
import os
import anthropic
from autonomize_observer import monitor

# Set environment variables
os.environ["MLFLOW_TRACKING_URI"] = "https://your-mlflow-server.com"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

# Create Anthropic client
client = anthropic.Anthropic()

# Enable monitoring with explicit provider specification
monitor(client, provider="anthropic")

# Use the client normally
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "What is machine learning?"}
    ]
)

print(response.content[0].text)
```

## Package Structure

- `autonomize_observer.tracing`: MLflow tracing and span management
- `autonomize_observer.monitoring`: Async monitoring, cost tracking, and client monitoring  
- `autonomize_observer.core`: MLflow client management and core exceptions

## Examples

See `examples/notebooks/` for detailed examples:
- Basic monitoring setup
- Advanced tracing workflows  
- Custom cost configurations

## Configuration

### Setting Up Credentials

The SDK supports different authentication methods:

#### Option 1: Direct MLflow Server
```python
import os
os.environ["MLFLOW_TRACKING_URI"] = "https://your-mlflow-server.com"
```

#### Option 2: Modelhub Integration
```python
import os
os.environ["MODELHUB_URI"] = "https://your-modelhub-url.com"
os.environ["MODELHUB_AUTH_CLIENT_ID"] = "your-client-id"
os.environ["MODELHUB_AUTH_CLIENT_SECRET"] = "your-client-secret"
```

### Custom Cost Rates

Configure custom cost rates for different models:

```python
from autonomize_observer.monitoring import CostTracker

# Define custom cost rates ($ per 1K tokens)
custom_rates = {
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    "claude-3-opus": {"input": 15.0, "output": 75.0},
    "my-custom-model": {"input": 0.25, "output": 0.75}
}

# Initialize cost tracker with custom rates
cost_tracker = CostTracker(cost_rates=custom_rates)
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MLFLOW_TRACKING_URI` | MLflow server URL | Yes (if not using Modelhub) |
| `MODELHUB_URI` | Modelhub server URL | Yes (if not using direct MLflow) |
| `MODELHUB_AUTH_CLIENT_ID` | Modelhub client ID | Yes (if using Modelhub) |
| `MODELHUB_AUTH_CLIENT_SECRET` | Modelhub client secret | Yes (if using Modelhub) |
| `AUTONOMIZE_EXPERIMENT_NAME` | Default experiment name | No |
| `OPENAI_API_KEY` | OpenAI API key | Yes (for OpenAI) |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes (for Anthropic) |

## Recent Improvements ✅

- **Async Client Detection**: Fixed async client detection across OpenAI, Azure OpenAI, and Anthropic
- **Consistent Metrics**: Unified naming with `input_tokens`, `output_tokens`, `total_cost` across all systems
- **Production Ready**: Robust error handling and multi-provider support

## Known Limitations

- **Test Coverage**: Comprehensive test suite in development

## What's Next

- API-based tracing (replacing Kafka)
- Comprehensive test coverage
- Performance optimizations

## 🎯 Compatibility Matrix

| Component | Status | Notes |
|-----------|--------|-------|
| **Genesis Studio Agents** | ✅ Fully Compatible | Seamless integration |
| **Langflow** | ✅ Fully Compatible | Shares streaming limitation |
| **OpenAI** | ✅ Ready | Sync + Async support |
| **Azure OpenAI** | ✅ Ready | Full feature parity |
| **Anthropic** | ✅ Ready | Claude models supported |
| **Python 3.12+** | ✅ Fully Supported | Type hints included |
| **MLflow 2.21-3.1** | ✅ Tested & Verified | All versions supported |

## License

Proprietary © Autonomize.ai