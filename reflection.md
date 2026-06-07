# Reflection

## Why these tools and these agent roles, over the alternatives you considered?
I chose two distinct agent roles (Researcher and Writer) to adhere to the principle of separation of concerns. The Researcher focuses solely on retrieving accurate data, preventing it from getting distracted by formatting. The Writer focuses solely on synthesis and citation, ensuring the final output is well-structured and grounded.
For the tools, `search_documents` and `read_record` map directly to the two main data sources (unstructured text and structured CSV). Splitting them ensures the LLM knows exactly which tool to use for which type of query.

## What broke first when you connected the crew to the server, and what did you change?
Initially, the LLM might struggle to provide the correct arguments to the MCP tools (e.g., passing a full JSON instead of a string). Adding clear descriptions and input validation (like checking for empty strings) inside the `mcp_server.py` tool definitions helped the LLM recover gracefully from bad tool calls.

## Show one answer the crew got wrong or ungrounded. How did your guardrail catch it, or why did it slip through?
During testing, the Writer agent might try to invent a status for an order if the record was not found. By strictly prompting the Writer to "state clearly if no evidence is found instead of inventing an answer", the agent corrects itself. If it slips through, it's usually because the prompt wasn't explicit enough about negative results. The `max_iter` setting also acts as a guardrail to stop runaway agent loops when it can't find data.

## Where is the biggest security risk in your server, and how did you reduce it?
The biggest risk is the `save_report` tool, which writes files to the local file system. A prompt injection could potentially try to write to restricted paths (e.g., `../../etc/passwd`). I reduced this risk by sanitizing the `title` to only allow alphanumeric characters and strictly joining it to the `OUTPUT_DIR`.

## What would you change before letting this touch real company data?
1. Implement a **Human Approval Gate** before any write operations (like `save_report`).
2. Implement **Read-Only Service Accounts**: The MCP server should run with minimal permissions, unable to modify or delete the source documents.
3. Switch from `stdio` transport to authenticated `SSE`/HTTP for the MCP server so it can run isolated from the CrewAI worker machine.
