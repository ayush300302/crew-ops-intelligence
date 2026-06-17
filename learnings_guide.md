# Learnings Guide — Operations Assistant (CrewAI + MCP)

This guide documents the key conceptual and practical engineering lessons learned during the development, debugging, and deployment of the **Operations Assistant** multi-agent application.

---

## 1. The Model Context Protocol (MCP)

### What is MCP?
The Model Context Protocol (created by Anthropic) is an open standard that enables developers to build secure, bidirectional connections between LLM agents and local or remote data sources and systems.

### Core Concepts Learned:
* **The Client-Server Architecture**: The MCP server exposes tools, resources, and prompts. The client (in our case, the CrewAI framework via `MCPServerAdapter`) connects to the server and delegates actions to it.
* **Transports**:
  * `stdio`: Standard Input/Output. The client spawns the server as a child process and communicates via JSON-RPC over stdin/stdout. Simple and highly secure for local execution.
  * `SSE` (Server-Sent Events): HTTP-based transport for remote services.
* **FastMCP**: Utilizing the FastMCP SDK simplifies server creation by using python decorators (`@mcp.tool()`) to automatically generate JSON schemas that describe tool inputs and outputs.

---

## 2. Multi-Agent System Design (CrewAI)

### Key Architectural Lessons:
* **Separation of Concerns**: Instead of a single agent doing everything, we designed a **two-agent crew**:
  1. **Operations Researcher**: Dedicated strictly to gathering facts from documents and records.
  2. **Operations Report Writer**: Dedicated strictly to compiling and formatting the final report with citations.
  This prevents "cognitive overload" in the LLM, leading to cleaner code execution and higher factual accuracy.
* **Sequential Process**: The output of the Researcher task is passed directly as context to the Writer task.

---

## 3. Real-World Debugging & Pivots (The "Gotchas")

Developing agentic workflows is notoriously complex. We resolved several core integration failures:

### A. Python Version Limits
* **Failure**: Initially attempted to run using Python 3.14. CrewAI relies on older versions of Pydantic and dependencies that do not support Python 3.14.
* **Fix**: Created a dedicated virtual environment running **Python 3.12** (`py -3.12 -m venv venv`), which is the sweet spot for modern agent frameworks.

### B. LLM Rate Limits & Provider Pivots
* **Failure**: The Gemini free-tier API has a strict 15 Requests Per Minute (RPM) limit. Since CrewAI runs autonomous thought loops, a single query can generate 10+ rapid LLM calls, causing immediate rate-limit exhaustion.
* **Fix**: Switched to **Groq** (`groq/llama-3.1-8b-instant`), which provides a generous free tier (30 RPM, 131K tokens/minute) and near-instant latency.

### C. API Parameter Incompatibility (The cache_breakpoint bug)
* **Failure**: CrewAI automatically appends Anthropic-style headers (`cache_breakpoint` / `cache_control`) into its outbound message content. When using Groq (via LiteLLM), the Groq API rejected these headers with validation errors.
* **Fix**: Wrote a custom monkey-patch in Python targeting `litellm.completion`. This wrapper dynamically strips the `cache_breakpoint` key from all message dicts before they are sent to the provider.

### D. Tool Isolation (Logical Guardrails)
* **Failure**: If all tools (`search_documents`, `read_record`, `save_report`) are given to both agents, the Writer agent will try to use the search tools itself. Because LLMs are prone to verbose searches, the Writer passed long queries like `"x100 router warranty period and recent issues"` to our substring-matching tool, returning empty results.
* **Fix**: Filtered and isolated the tools:
  * Researcher Tools: `[search_documents, read_record]`
  * Writer Tools: `[save_report]`
  This forces the Writer to rely *only* on the clean facts verified by the Researcher.

---

## 4. Security & Robustness

* **Path Traversal Mitigation**: The `save_report` tool writes files to the disk. A malicious file/prompt injection could pass a title containing `../` to overwrite system files. We sanitized the file title to allow alphanumeric characters only.
* **Runaway Loop Control**: Set `max_iter=10` on all agents to ensure that if they fail to resolve a task, they stop and report the error instead of burning through API tokens forever.
* **Windows Console Encoding**: CrewAI prints progress emojis (🚀, 📋, ✅). On Windows PowerShell, stdout defaults to `cp1252` encoding, throwing `charmap codec can't encode character` errors. We fixed this by programmatically reconfiguring standard output to `UTF-8` inside `crew.py`.

---

## 5. Visual Prototyping

* **Mermaid Integration**: We learned to use Mermaid.js block markup to generate complex, visually appealing architecture and sequence diagrams directly inside markdown documentation.
* **Dynamic Styling**: By using Mermaid's `config` frontmatter and `classDef` CSS definitions, we transformed default layouts into beautiful, premium dark-themed diagrams.
