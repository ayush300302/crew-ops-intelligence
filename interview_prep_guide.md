# Interview Preparation Guide — Operations Assistant

Use this guide to talk about this project confidently during technical interviews. It is structured using the **STAR method** (Situation, Task, Action, Result) to showcase strong engineering leadership and problem-solving skills.

---

## 1. The Elevator Pitch (How to introduce the project)

### The 30-Second Pitch:
> "I built an autonomous **Operations Assistant** that solves a major enterprise problem: manual data silo crossing. The system uses a multi-agent **CrewAI** team that connects dynamically to a custom **Model Context Protocol (MCP)** server. The server exposes local specifications, tickets, and database records via secure tools over `stdio`. The agents collaborate: one researches the specifications, the other writes and saves a fully grounded business report with exact source citations. It runs locally, uses Groq Llama-3.1, and includes security measures like path-traversal sanitization and agent loop boundaries."

### The 2-Minute Deep Dive:
> "The core objective of the project was to automate manual lookup tasks for operations teams who frequently jump between unstructured specs sheet documents, support tickets, and structured inventory databases. 
> 
> To solve this, I designed a decoupled architecture. On the backend, I built an MCP server using FastMCP, exposing tools to perform keyword searches in documents and dict-lookups in CSVs. On the client side, I orchestrated a sequential CrewAI crew. I isolated the agents by their capabilities: the Operations Researcher gathers raw evidence from the MCP server, and the Report Writer synthesizes this data into a formatted report, saving it via a restricted filesystem tool. 
> 
> Along the way, I overcame several real-world LLM orchestration challenges, including handling rate limits, monkey-patching compatibility issues with Groq APIs, and implementing strict security boundaries to prevent path traversal and runaway execution loops."

---

## 2. Architectural Highlights (Why these patterns matter)

* **Why MCP (Model Context Protocol) over custom APIs?**
  * *Interview Answer*: "Standard custom APIs lock you into a single framework. MCP is an open-standard protocol. By exposing our databases through an MCP server, our tools become completely model-agnostic. Tomorrow, we could swap CrewAI for LangChain, AutoGen, or Claude Desktop, and the connection layer remains identical."
* **Why Multi-Agent (2 Agents) instead of 1 large prompt?**
  * *Interview Answer*: "Single LLM prompts suffer from 'attention loss' and formatting distractions when performing multi-step tasks. By dividing responsibilities—separating the **Researcher** (gathering raw text) from the **Writer** (structuring and citing)—we drastically reduce hallucinations and improve report accuracy."

---

## 3. Technical STAR Stories (Use these to answer "Tell me about a time you solved a hard technical problem...")

### Story 1: Solving the Outbound API Parameter Validation Bug (Groq vs. CrewAI)
* **Situation**: CrewAI uses LiteLLM under the hood. When configuring Groq (`llama-3.1-8b-instant`), CrewAI automatically injected Anthropic-specific parameters (`cache_breakpoint` and `cache_control` headers) into the message body. 
* **Task**: Groq's API endpoint is strictly OpenAI-compatible and crashed with validation errors when receiving these unrecognized cache parameters.
* **Action**: I wrote a custom runtime monkey-patch targeting the `litellm.completion` method. The patch intercepts outbound requests, recursively traverses the messages list, and strips out `cache_breakpoint` and `cache_control` keys before they reach the Groq API.
* **Result**: The system ran successfully on Groq with sub-second latency and zero API crashes, circumventing the rigid constraints of the agent library.

### Story 2: Preventing Grounding Pollution (Tool Isolation)
* **Situation**: In initial tests, all tools were passed globally to all agents. When writing the report, the Writer agent would attempt to run search queries itself. Because LLMs tend to be verbose, the Writer queried the substring-matching tool with long phrases like *"x100 router warranty period and recent issues"*, which failed to match, overwriting the researcher's findings with "not found".
* **Task**: Restrict tool usage to maintain clean grounding boundaries.
* **Action**: I refactored the initialization script to filter the tools returned by the `MCPServerAdapter`. I created separate lists: the Researcher received `search_documents` and `read_record`, and the Writer was restricted solely to the `save_report` tool.
* **Result**: This enforced a strict boundary. The Writer was forced to rely *exclusively* on the facts verified by the Researcher, eliminating redundant searches and grounding failures.

### Story 3: Mitigating Security Risks (Path Traversal & Runaway Loops)
* **Situation**: The `save_report` tool accepts a filename title and content from the Writer agent to save locally. Because agent outputs are untrusted, a malicious input could inject directory traversal sequences like `../../` to overwrite critical system configuration files.
* **Task**: Build robust defense-in-depth security guardrails.
* **Action**: I implemented a two-fold mitigation: 
  1. Sanitized the `title` parameter in `mcp_server.py` using character filtering to only allow alphanumeric characters and underscores.
  2. Implemented strict directory containment joining the title directly to our output folder path. 
### Story 4: Automating Deployment with a Secure CI/CD Containerization Pipeline
* **Situation**: The application requires a precise Python environment (Python 3.12) and multiple complex dependencies (CrewAI, FastMCP, LiteLLM) to run. Without containment, manual local execution led to cross-platform compatibility issues, configuration drift, and untested deployments.
* **Task**: Create a unified execution environment and automate the validation and deployment process so that every commit is tested and the package is built into a deployable container image automatically.
* **Action**: 
  1. I created a secure, lightweight `Dockerfile` using `python:3.12-slim` that isolates the execution dependencies and runs the agent crew orchestration by default.
  2. I configured a multi-job **GitHub Actions** CI/CD pipeline. The first job (`test`) runs pytest on any push/PR to verify code health. The second job (`deploy`) triggers only on successful merges to the `main` branch, authenticates securely with GitHub Container Registry (GHCR) using the built-in `GITHUB_TOKEN`, and pushes the tagged Docker image.
* **Result**: Automated delivery of the application. Developers get instant feedback on code stability, and operations teams can instantly run the fully configured agent container anywhere via a single `docker run` command.

---

## 4. Tough Interview Q&A

### Q: "Why containerize a Python MCP server / agent team?"
> "Python agent frameworks have deep dependency trees (such as Pydantic, LiteLLM, and system network utilities) that are highly sensitive to operating system versions and interpreter runtimes. By packaging the app inside Docker, we enforce standard execution on `python:3.12-slim` across all development and production environments. It also simplifies local deployment for end-users, since they only need Docker installed and do not need to manage virtual environments or Python packages."

### Q: "How did you secure your CI/CD pipeline credentials?"
> "I followed the principle of least privilege by using the built-in `${{ secrets.GITHUB_TOKEN }}` provided dynamically by GitHub Actions. Rather than hardcoding personal registry credentials or long-lived API keys, this token is temporary, automatically rotated, and scoped only to write to GitHub Packages (`packages: write`) for this specific repository. External API keys (like `GROQ_API_KEY`) are kept completely out of the image build and are injected safely as runtime environment variables during container launch."

### Q: "How would you scale this system to handle 100,000 documents instead of 10?"
> "A simple keyword substring-match (`glob` search) will not scale to 100,000 files because it is `O(N)` and introduces high I/O latency. I would evolve the architecture by:
> 1. Replacing the simple document lookup tool with a **Retrieval-Augmented Generation (RAG)** pipeline. I would chunk the documents, generate vector embeddings, and store them in a vector database like pgvector, Chroma, or Pinecone.
> 2. The MCP server would expose a `similarity_search` tool that queries this vector store.
> 3. I would implement caching on the MCP server layer (e.g. Redis) to store common queries."

### Q: "Why did you choose `stdio` transport instead of HTTP/SSE?"
> "`stdio` is ideal for local, single-machine execution because the server runs as a direct subprocess of the client, removing the need to manage port allocations, network security firewalls, or user authentication. If we wanted to deploy this server as a centralized shared resource for multiple teams, I would configure FastMCP to run over **SSE (Server-Sent Events)**, wrapping it in an authenticated API gateway."

### Q: "How did you test and validate this system?"
> "I implemented tests at two levels:
> 1. **Unit Tests (`pytest`)**: Targeting the MCP tools directly to verify input validation (e.g., handling empty queries, missing record IDs, file writing success).
> 2. **Integration Tests**: Running mock executions to ensure the adapter boots the server successfully and the sequential handover between the agents functions without crashing.
> 3. **Manual Validation**: Checking the generated output report against the source documents to verify zero factual hallucinations."

