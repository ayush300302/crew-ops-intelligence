# Operations Assistant

A multi-agent CrewAI crew on an MCP server.

## Overview
This project implements a CrewAI crew that connects to an MCP server built with FastMCP. The crew reads local documents and a CSV file using the MCP server tools, and generates a sourced report answering a business question.

## Setup

1. **Clone the repository** (or run from this fresh clone):
   ```bash
   git clone <repo-url>
   cd operations-assistant
   ```

2. **Set up the Python environment**:
   Using Python 3.11+ is recommended. You can use `uv` or `venv`:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys (e.g., Gemini or OpenAI). If using Ollama, ensure it is running locally.
   ```bash
   cp .env.example .env
   ```

## Running the Project

### 1. Run the MCP Server (Inspector)
You can run the MCP Inspector to test the tools:
```bash
mcp dev mcp_server.py
```

### 2. Run the CrewAI Crew
To execute the task:
```bash
python crew.py
```

## Structure
- `mcp_server.py`: FastMCP server exposing tools over local data.
- `crew.py`: CrewAI agents connecting to the MCP server via `MCPServerAdapter`.
- `data/`: Contains sample text documents and a CSV file of records.
- `output/`: Where the generated reports are saved.
- `tests/`: Unit tests and end-to-end tests.
