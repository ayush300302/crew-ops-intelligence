# Operations Assistant

A multi-agent CrewAI crew on an MCP server.

## Overview
This project implements a CrewAI crew that connects to an MCP server built with FastMCP. The crew reads local documents and a CSV file using the MCP server tools, and generates a sourced report answering a business question.

## Architecture

```mermaid
graph TB
    User["User runs crew.py"]

    subgraph CrewAI_Framework["CrewAI Framework"]
        Crew["Crew Orchestrator"]
        Researcher["Researcher Agent"]
        Writer["Writer Agent"]
    end

    subgraph LLM_Provider["LLM Provider"]
        Groq["Groq API - llama-3.1-8b-instant"]
    end

    subgraph MCP_Server["MCP Server - FastMCP over stdio"]
        Tool1["search_documents - keyword search in .txt"]
        Tool2["read_record - lookup by ID in CSV"]
        Tool3["save_report - write markdown to output"]
    end

    subgraph Data_Store["Local Data Store"]
        Docs["data/documents/*.txt"]
        CSV["data/records.csv"]
    end

    subgraph Output_Store["Output"]
        Report["output/*.md"]
    end

    User --> Crew
    Crew --> Researcher
    Researcher -->|findings| Writer

    Researcher <-->|tool calls| Tool1
    Researcher <-->|tool calls| Tool2
    Writer <-->|tool calls| Tool3

    Researcher <-->|inference| Groq
    Writer <-->|inference| Groq

    Tool1 <--> Docs
    Tool2 <--> CSV
    Tool3 --> Report
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as crew.py
    participant R as Researcher Agent
    participant W as Writer Agent
    participant LLM as Groq LLM
    participant MCP as MCP Server
    participant D as Data Store

    U->>C: python crew.py
    C->>MCP: Start MCP server via stdio
    MCP-->>C: Connected

    C->>R: Start research task
    R->>LLM: What tools should I use?
    LLM-->>R: Call search_documents with warranty
    R->>MCP: search_documents warranty
    MCP->>D: Search txt files for warranty
    D-->>MCP: product_specs_x100.txt
    MCP-->>R: Warranty period is 2 years

    R->>LLM: Next step
    LLM-->>R: Call search_documents with acme
    R->>MCP: search_documents acme
    MCP->>D: Search txt files for acme
    D-->>MCP: support_ticket_001.txt
    MCP-->>R: Firmware updated to v2.1

    R->>LLM: Next step
    LLM-->>R: Call read_record R001
    R->>MCP: read_record R001
    MCP->>D: Lookup R001 in CSV
    D-->>MCP: Acme Corp 5 units Shipped
    MCP-->>R: Record details

    R-->>C: Research findings with citations

    C->>W: Start report task
    W->>LLM: Write report from findings
    LLM-->>W: Markdown report draft
    W->>MCP: save_report Acme_Corp_X100_Report
    MCP->>D: Write to output folder
    MCP-->>W: Success Report saved

    W-->>C: Task complete
    C-->>U: Report saved to output
```

## Security Model

```mermaid
graph TD
    subgraph Threats["Threat Surface"]
        T1["Path Traversal via save_report"]
        T2["Empty or Malicious Inputs"]
        T3["Runaway Agent Loops"]
        T4["API Key Exposure"]
        T5["Prompt Injection in Documents"]
    end

    subgraph Mitigations["Mitigations Applied"]
        M1["Title sanitized to alphanumeric only"]
        M2["All tools validate inputs and return errors"]
        M3["max_iter=10 on all agents"]
        M4[".env in .gitignore and .env.example has placeholders"]
        M5["Task prompts enforce citation-only answers"]
    end

    T1 --> M1
    T2 --> M2
    T3 --> M3
    T4 --> M4
    T5 --> M5
```

## Tech Stack

```mermaid
graph BT
    subgraph Stack["Technology Stack"]
        L1["Python 3.12"]
        L2["FastMCP - MCP Server"]
        L3["CrewAI - Agent Framework"]
        L4["LiteLLM - LLM Routing"]
        L5["Groq - LLM Provider"]
        L6["pytest - Testing"]
    end

    L1 --> L2
    L1 --> L3
    L3 --> L4
    L4 --> L5
    L1 --> L6
```

## Setup

1. **Clone the repository**:
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
```bash
mcp dev mcp_server.py
```

### 2. Run the CrewAI Crew
```bash
python crew.py
```

### 3. Run Tests
```bash
python -m pytest tests/ -v
```

## Project Structure
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
