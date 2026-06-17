# Operations Assistant

A multi-agent CrewAI crew on an MCP server.

## Overview
This project implements a CrewAI crew that connects to an MCP server built with FastMCP. The crew reads local documents and a CSV file using the MCP server tools, and generates a sourced report answering a business question.

## Architecture

See [HLD.md](HLD.md) for the full High-Level Design with architecture and sequence diagrams.

## Setup

1. **Clone the repository** (or run from this fresh clone):
   ```bash
   git clone <repo-url>
   cd operations-assistant
   ```

2. **Set up the Python environment** (Python 3.11 or 3.12 required):
   ```bash
   py -3.12 -m venv venv
   venv\Scripts\activate        # On Windows
   # source venv/bin/activate   # On macOS/Linux
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API key:
   ```bash
   cp .env.example .env
   ```
   Recommended: Get a free **Groq API key** from https://console.groq.com

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

### 3. Run Tests
```bash
python -m pytest tests/ -v
```

## Structure
- `mcp_server.py`: FastMCP server exposing tools over local data.
- `crew.py`: CrewAI agents connecting to the MCP server via `MCPServerAdapter`.
- `data/`: Contains sample text documents and a CSV file of records.
- `output/`: Where the generated reports are saved.
- `tests/`: Unit tests and end-to-end tests.
- `HLD.md`: High-Level Design with architecture diagrams.
- `reflection.md`: Design decisions, failures, and lessons learned.

## LLM Configuration
The project uses **Groq** (free tier) with `llama-3.1-8b-instant` by default. You can switch to other providers by modifying `crew.py`:
- Groq: Set `GROQ_API_KEY` in `.env`
- Gemini: Set `GEMINI_API_KEY` in `.env`
- OpenAI: Set `OPENAI_API_KEY` in `.env`

## License

Educational / hackathon project.
