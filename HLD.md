# High-Level Design (HLD) — Operations Assistant

## Architecture Overview

This project implements a **multi-agent AI system** that connects to a local MCP (Model Context Protocol) server to answer business questions using local documents and structured data.

```mermaid
graph TB
    subgraph User["👤 User"]
        Q["Business Question"]
    end

    subgraph CrewAI["🤖 CrewAI Framework"]
        direction TB
        CR["crew.py"]
        
        subgraph Agents["Agent Pipeline (Sequential)"]
            direction LR
            R["🔍 Researcher Agent<br/><i>Role: Find facts</i><br/><i>Goal: Accurate retrieval</i>"]
            W["✍️ Writer Agent<br/><i>Role: Synthesize report</i><br/><i>Goal: Sourced markdown</i>"]
        end

        subgraph LLM["☁️ LLM Provider"]
            G["Groq API<br/><i>llama-3.1-8b-instant</i><br/><i>Free tier: 30 RPM</i>"]
        end
    end

    subgraph MCP["🔧 MCP Server (FastMCP via stdio)"]
        MS["mcp_server.py"]
        
        subgraph Tools["Exposed Tools"]
            T1["🔎 search_documents<br/><i>Keyword search in .txt files</i>"]
            T2["📋 read_record<br/><i>Lookup by ID in CSV</i>"]
            T3["💾 save_report<br/><i>Write markdown to output/</i>"]
        end
    end

    subgraph Data["📁 Local Data Store"]
        D1["data/documents/*.txt<br/><i>Policies, specs, tickets</i>"]
        D2["data/records.csv<br/><i>Orders and inventory</i>"]
    end

    subgraph Output["📄 Output"]
        O1["output/*.md<br/><i>Generated reports</i>"]
    end

    Q --> CR
    CR --> R
    R -->|"Findings"| W
    R <-->|"Tool Calls"| MS
    W <-->|"Tool Calls"| MS
    R <--> G
    W <--> G
    T1 <--> D1
    T2 <--> D2
    T3 --> O1

    style User fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style CrewAI fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style MCP fill:#fff3e0,stroke:#e65100,color:#bf360c
    style Data fill:#f3e5f5,stroke:#6a1b9a,color:#4a148c
    style Output fill:#fce4ec,stroke:#c62828,color:#b71c1c
    style Agents fill:#e8eaf6,stroke:#283593
    style Tools fill:#fff8e1,stroke:#f57f17
    style LLM fill:#e0f7fa,stroke:#00695c
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as 🤖 crew.py
    participant R as 🔍 Researcher
    participant W as ✍️ Writer
    participant LLM as ☁️ Groq LLM
    participant MCP as 🔧 MCP Server
    participant D as 📁 Data Store

    U->>C: Run crew.py
    C->>MCP: Start MCP server (stdio)
    MCP-->>C: Connected

    C->>R: Start research task
    R->>LLM: "What tools should I use?"
    LLM-->>R: Call search_documents("warranty")
    R->>MCP: search_documents("warranty")
    MCP->>D: Search *.txt for "warranty"
    D-->>MCP: product_specs_x100.txt
    MCP-->>R: "Warranty period is 2 years"

    R->>LLM: "Next step?"
    LLM-->>R: Call search_documents("acme")
    R->>MCP: search_documents("acme")
    MCP->>D: Search *.txt for "acme"
    D-->>MCP: support_ticket_001.txt
    MCP-->>R: "Firmware updated to v2.1"

    R->>LLM: "Next step?"
    LLM-->>R: Call read_record("R001")
    R->>MCP: read_record("R001")
    MCP->>D: Lookup R001 in CSV
    D-->>MCP: Acme Corp, 5 units, Shipped
    MCP-->>R: Record details

    R-->>C: Research findings with citations

    C->>W: Start report task
    W->>LLM: "Write report from findings"
    LLM-->>W: Markdown report draft
    W->>MCP: save_report("Acme_Corp_X100_Report", content)
    MCP->>D: Write to output/
    MCP-->>W: "Success! Report saved"

    W-->>C: Task complete
    C-->>U: Report saved to output/
```

## Component Details

| Component | File | Responsibility |
|-----------|------|----------------|
| **MCP Server** | `mcp_server.py` | Exposes 3 tools over stdio transport using FastMCP |
| **Crew Orchestrator** | `crew.py` | Configures agents, tasks, and LLM; runs the sequential crew |
| **Sample Data** | `data/` | 10 text documents + 15-row CSV of inventory records |
| **Unit Tests** | `tests/test_mcp.py` | Tests all 3 MCP tools directly (search, read, save) |
| **E2E Test** | `tests/test_crew.py` | Smoke test for crew importability |
| **Output** | `output/` | Where generated markdown reports are saved |

## Security Measures

| Risk | Mitigation |
|------|------------|
| Path traversal via `save_report` title | Title sanitized to alphanumeric only |
| Empty/malicious tool inputs | All tools validate inputs, return clear error messages |
| Runaway agent loops | `max_iter=10` on all agents |
| API key exposure | `.env` in `.gitignore`; `.env.example` has placeholders only |
| Prompt injection in documents | Task prompts enforce citation-only answers; no fabrication |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| MCP Server | FastMCP (mcp SDK) |
| Agent Framework | CrewAI |
| LLM Provider | Groq (llama-3.1-8b-instant) |
| LLM Routing | LiteLLM |
| Testing | pytest |
| Config | python-dotenv |
