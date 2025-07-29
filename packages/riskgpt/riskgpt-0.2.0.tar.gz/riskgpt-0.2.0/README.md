# RiskGPT

[![PyPI version](https://badge.fury.io/py/riskgpt.svg)](https://pypi.org/project/riskgpt/)
[![PyPI](https://img.shields.io/pypi/v/riskgpt)](https://pypi.org/project/riskgpt/)
[![Linted by Ruff](https://img.shields.io/badge/lint-ruff-green.svg)](https://docs.astral.sh/ruff/)
[![Checked with mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![License: MIT](https://img.shields.io/pypi/l/riskgpt.svg)](https://github.com/thwolter/riskgpt/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/riskgpt)](https://pypi.org/project/riskgpt/)

## 🎯 Overview

RiskGPT provides utilities for analyzing project risks and opportunities using LLM-based chains. The package leverages LangChain and LangGraph to create sophisticated workflows for risk assessment, analysis, and mitigation planning.

## 🚀 Features

- Risk and opportunity identification and analysis
- Cost-benefit analysis for risk mitigation strategies
- External context enrichment through web search
- Circuit breaker pattern for resilient external API calls
- Conversation memory with multiple backend options
- Programmatic API for direct access to search and document services

## 📁 Project Structure

```
riskgpt/
├── src/                   # Source code directory
│   ├── riskgpt/           # Main package directory
│       ├── chains/        # LLM chain implementations
│       ├── config/        # Configuration settings
│       ├── helpers/       # Helper functions and utilities
│       ├── models/        # Data models and schemas
│       ├── processors/    # Input/output processors
│       ├── prompts/       # LLM prompts organized by function
│       ├── workflows/     # Risk assessment workflows
│       ├── api.py         # Public API functions
│       ├── logger.py      # Logging configuration
├── dist/                  # Distribution packages
│   ├── riskgpt-0.1.0-py3-none-any.whl  # Wheel package
│   └── riskgpt-0.1.0.tar.gz            # Source distribution
├── examples/              # Example notebooks and scripts
│   ├── challenge_and_enrich_workflow.ipynb  # Example workflow
│   ├── colab_usage_guide.ipynb         # Google Colab usage guide
│   ├── codespaces_usage_guide.ipynb    # GitHub Codespaces usage guide
│   ├── colab_setup.py                  # Setup script for Google Colab
│   └── visualize_enrich_context_graph.py  # Graph visualization example
├── tests/                 # Test directory
│   ├── functional/        # Functional tests
│   ├── integration/       # Integration tests
│   ├── unit/              # Unit tests
│   └── utils/             # Test utilities
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🛠️ Installation

You have several options to install RiskGPT:

### Option 1: Install using uv (Development)

Install dependencies using [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver:

```bash
uv sync
```

### Option 2: Install from wheel file

If you have the wheel file available in the dist folder:

```bash
pip install dist/riskgpt-0.1.0-py3-none-any.whl
```

### Option 3: Install from GitHub (for users)

```bash
pip install git+https://github.com/thwolter/riskgpt.git
```

## 💡 Usage

Basic usage example:

```python
from riskgpt import configure_logging
from riskgpt.models.common import BusinessContext
from riskgpt.workflows.risk_workflow import risk_workflow
from riskgpt.models.chains import RiskRequest

# Configure logging
configure_logging()

# Create a business context
context = BusinessContext(
    project_id="ACME-1",
    project_name="ACME Corp Security Upgrade",
    project_description="Implement new cybersecurity measures across all departments"
)

# Create a risk request
request = RiskRequest(
    business_context=context,
    category="cybersecurity"
)

# Run the risk workflow (async function)
import asyncio
result = asyncio.run(risk_workflow(request))
```

### Google Colab Usage

To use RiskGPT in Google Colab notebooks, you have two options:

#### Option 1: Step-by-step guide

See the [Colab usage guide](examples/colab_usage_guide.ipynb) which provides detailed instructions for:

- Installing RiskGPT directly from GitHub
- Setting up the OpenAI API key in Colab
- Running basic and advanced examples
- Troubleshooting common issues

#### Option 2: Quick setup script

For a faster setup, run this command in a Colab cell:

```python
!curl -s https://raw.githubusercontent.com/thwolter/riskgpt/main/examples/colab_setup.py | python3
```

This script will:
- Check and install Python 3.12 if needed
- Install RiskGPT from GitHub
- Help you set up your OpenAI API key
- Provide a basic usage example

### GitHub Codespaces Usage

To use RiskGPT in GitHub Codespaces, follow these steps:

#### Option 1: Step-by-step guide

See the [Codespaces usage guide](examples/codespaces_usage_guide.ipynb) which provides detailed instructions for:

- Installing RiskGPT directly from GitHub
- Setting up the OpenAI API key in Codespaces
- Running basic and advanced examples
- Local development in Codespaces
- Troubleshooting common issues

#### Option 2: Setting up OpenAI API key as a Codespaces secret

For better security, you can add your OpenAI API key as a Codespaces secret:

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Codespaces
3. Click "New repository secret"
4. Name: `OPENAI_API_KEY`
5. Value: Your OpenAI API key
6. Click "Add secret"

Then in your Codespaces Jupyter notebook or Python script:

```python
# Install RiskGPT directly from GitHub
!pip install git+https://github.com/thwolter/riskgpt.git

# The API key will be automatically available as an environment variable
```

Validation helpers are available in `riskgpt.processors.input_validator` to convert dictionaries into request objects:

```python
from src import validate_risk_request

request_dict = {"project_id": "ACME-1", "project_name": "Security Upgrade", ...}
validated_request = validate_risk_request(request_dict)
```

## 🔧 Configuration

RiskGPT loads configuration from environment variables using a `.env` file at the project root or the regular environment.

Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Available environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | – | API key for the OpenAI service. Required to use the real model; otherwise a dummy model is used. |
| `OPENAI_MODEL_NAME` | `openai:gpt-4.1-nano` | Name of the OpenAI chat model. |
| `TEMPERATURE` | `0.7` | Temperature parameter for the model's response. Higher values make the output more random. |
| `MAX_TOKENS` | – | Maximum number of tokens in the model's response. This value might be adjusted depending on the model being used. |
| `MEMORY_TYPE` | `buffer` | Conversation memory backend. Choose `none`, `buffer` or `redis`. |
| `REDIS_URL` | – | Redis connection string. Needed when `MEMORY_TYPE` is set to `redis`. |
| `DEFAULT_PROMPT_VERSION` | `v1` | Version identifier for prompts under `riskgpt/prompts`. |
| `SEARCH_PROVIDER` | `duckduckgo` | Search provider for external context enrichment. Choose `duckduckgo`, `google`, `wikipedia`, or `tavily`. |
| `MAX_SEARCH_RESULTS` | `3` | Maximum number of search results to return. |
| `INCLUDE_WIKIPEDIA` | `False` | Whether to include Wikipedia results in addition to the primary search provider. |
| `GOOGLE_CSE_ID` | – | Google Custom Search Engine ID. Required when `SEARCH_PROVIDER` is set to `google`. |
| `GOOGLE_API_KEY` | – | Google API key. Required when `SEARCH_PROVIDER` is set to `google`. |
| `TAVILY_API_KEY` | – | Tavily API key. Required when `SEARCH_PROVIDER` is set to `tavily`. |
| `DOCUMENT_SERVICE_URL` | – | Base URL of the document microservice used to retrieve relevant documents in the risk workflow. |

## 🔄 Circuit Breaker Pattern

RiskGPT implements a circuit breaker pattern for external API calls to handle service outages gracefully. The circuit breaker prevents sending requests to services that are likely to fail, reducing latency and conserving resources.

The circuit breaker is implemented for:
- OpenAI API calls in the `BaseChain` class
- Search API calls (DuckDuckGo, Google Custom Search, Wikipedia) in the external context enrichment workflow

When the circuit is open (after multiple failures), the application will use fallback mechanisms:
- For OpenAI: Returns a minimal valid response with an error message
- For search providers: Returns empty results and continues with other data sources

## 🧪 Development

Install the pre-commit hooks once:

```bash
pre-commit install
```

The hooks run ruff and mypy on each commit. Tests are executed with `pytest` and coverage is measured via `pytest-cov`.

Run the full test suite locally with:

```bash
uv run pytest --cov=src
```

Unit tests run by default when executing `pytest`:

```bash
uv run pytest
```

Integration tests require real external services and valid API keys:

```bash
export OPENAI_API_KEY=sk-test-123
export DOCUMENT_SERVICE_URL=https://example.com
uv run pytest -m integration
```

## 📚 Programmatic API

RiskGPT exposes helper functions to access search and document services directly:

```python
from riskgpt.api import search_context, fetch_documents
from riskgpt.models.common import BusinessContext
from riskgpt.models.utils.search import SearchRequest

# Search recent news
search_req = SearchRequest(query="ACME Corp cybersecurity", context_type="news")
search_response = search_context(search_req)

# Retrieve project documents
context = BusinessContext(project_id="ACME-1")
doc_uuids = fetch_documents(context)  # Returns list of document UUIDs
```

## 📄 License

RiskGPT is distributed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
