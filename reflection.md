# Reflection

## Why these tools and these agent roles, over the alternatives you considered?
I chose two distinct agent roles (Researcher and Writer) to adhere to the principle of separation of concerns. The Researcher focuses solely on retrieving accurate data, preventing it from getting distracted by formatting. The Writer focuses solely on synthesis and citation, ensuring the final output is well-structured and grounded.
For the tools, `search_documents` and `read_record` map directly to the two main data sources (unstructured text and structured CSV). Splitting them ensures the LLM knows exactly which tool to use for which type of query. `save_report` was added as a third tool to persist the final output.

## What broke first when you connected the crew to the server, and what did you change?
Multiple issues occurred during integration:

1. **Python version incompatibility**: The project requires Python 3.11 or 3.12, but development initially used Python 3.14, which `crewai` does not support. Fixed by creating a venv with `py -3.12 -m venv venv`.

2. **LLM provider errors**: CrewAI defaults to OpenAI. Switching to Gemini required installing `crewai[google-genai]` and configuring the `LLM` class with the correct model name and API key.

3. **Gemini API quota exhaustion**: The free-tier Gemini API has strict rate limits (15 RPM), and CrewAI makes many rapid internal LLM calls. Even with retry logic and rate-limiting monkey patches on `litellm.completion`, the native `google-genai` provider bypassed our patches entirely. We resolved this by switching to **Groq** (`groq/llama-3.1-8b-instant`), which offers a generous free tier (30 RPM, 131K tokens/min).

4. **Unsupported parameters**: CrewAI sends Anthropic-style `cache_breakpoint` params that Groq rejects. Fixed by monkey-patching `litellm.completion` to strip these params from messages before forwarding, and setting `litellm.drop_params = True`.

5. **Poor search results**: The Researcher agent initially searched with long phrases like "warranty period for X100 Router", but `search_documents` uses simple substring matching. Fixed by updating the task prompt to instruct the agent to use short, single-word queries like "warranty" and "acme".

## Show one answer the crew got wrong or ungrounded. How did your guardrail catch it, or why did it slip through?
During early testing with the smaller `llama-3.1-8b-instant` model, the Writer agent generated a report stating "no information was found" for warranty and support tickets — even though the data existed. This happened because the Researcher used complex multi-word search queries that didn't match any documents. The guardrail of "state clearly if no evidence is found instead of inventing an answer" worked correctly (it didn't fabricate data), but the root cause was tool usage, not hallucination. We fixed this by adding explicit instructions on how to use the search tool with simple keywords.

## Where is the biggest security risk in your server, and how did you reduce it?
The biggest risk is the `save_report` tool, which writes files to the local file system. A prompt injection could potentially try to write to restricted paths (e.g., `../../etc/passwd`). I reduced this risk by sanitizing the `title` to only allow alphanumeric characters and strictly joining it to the `OUTPUT_DIR`.

## What would you change before letting this touch real company data?
1. Implement a **Human Approval Gate** before any write operations (like `save_report`).
2. Implement **Read-Only Service Accounts**: The MCP server should run with minimal permissions, unable to modify or delete the source documents.
3. Switch from `stdio` transport to authenticated `SSE`/HTTP for the MCP server so it can run isolated from the CrewAI worker machine.
4. Add **structured logging and observability** — save traces of every tool call with timings and token counts.
5. Add **input sanitization on search queries** — validate and limit the length/content of search strings to prevent injection via crafted document content.

## Decision Log
| Decision | Chosen | Rejected | Reason |
|----------|--------|----------|--------|
| Python version | 3.12 (venv) | 3.14 (system) | crewai requires <3.14 |
| LLM provider | Groq (free, fast) | Gemini (quota issues), OpenAI (paid) | Gemini free tier too restrictive for multi-agent workflows |
| LLM model | llama-3.1-8b-instant | llama-3.3-70b-versatile | 70b has only 6K tokens/min on free tier; 8b has 131K |
| Agent architecture | 2 agents (Researcher + Writer) | Single agent | Separation of concerns; easier to debug and extend |
| MCP transport | stdio | SSE/HTTP | Simpler for local development; PDF recommended approach |
| Search approach | Simple keyword substring matching | Embedding-based semantic search | Keeps the project lightweight and explainable |
