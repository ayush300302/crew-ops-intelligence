# 5-Minute Demo Video Script (Terminal Execution)

This script is structured exactly to match the **Section 10** requirements of the Week 14 assignment PDF. You can read this script aloud while recording your screen (using Loom, OBS, Zoom, or any screen recorder) showing your terminal.

---

## Part 1: The Pitch (~1 minute)
* **What to show on screen**: Have your terminal open in the `operations-assistant` folder, showing a clear, empty console prompt. You can also show the `README.md` file in your editor with the newly styled dark-theme architecture diagram.
* **What to say**:
  > "Hello, my name is Ayush, and today I’m demonstrating my Operations Assistant: a multi-agent system built using CrewAI that connects dynamically to a custom Model Context Protocol (or MCP) server.
  >
  > In a typical business setting, operations data is scattered—policies are in text spec sheets, support tickets are in markdown, and inventory records are locked in spreadsheet CSVs. Staff waste hours cross-checking these manually.
  >
  > The system I built automates this entirely. We expose these data sources as secure tools through a FastMCP server over a stdio connection. Then, a CrewAI crew composed of a Researcher agent and a Writer agent collaborates to find the facts, verify the inventory, and save a fully-cited markdown report in the output folder. This is laptop-runnable, secure, and utilizes the Groq Llama 3.1 model."

---

## Part 2: Show it Run (~1 minute)
* **What to show on screen**: Type `python crew.py` (or `venv\Scripts\python.exe crew.py` on Windows) in the terminal and press Enter. Let the log stream run live. Scroll to highlight agent thoughts.
* **What to say**:
  > "Let's see the system in action. I will run `python crew.py` in the terminal.
  > 
  > You can see the console logs starting up: the system successfully connects to the local FastMCP server. The Researcher agent starts by looking at the business question: *What is the warranty period for the X100 Router, and what was the ticket resolution and order status for Acme Corp?*
  > 
  > Watch the tool calls: The Researcher invokes `search_documents(query='warranty')` to query the spec sheets and finds the 2-year warranty in `product_specs_x100.txt`. 
  > 
  > Next, it automatically queries `search_documents(query='acme')` and extracts the resolution of ticket #001 in `support_ticket_001.txt` showing the firmware was updated to v2.1.
  > 
  > Finally, it calls `read_record(record_id='R001')` on our CSV inventory records and confirms Acme Corp has 5 units shipped.
  > 
  > The Researcher hands these clean facts to the Report Writer agent, which runs its task, compiles the markdown, and calls `save_report` to write the final document to the disk. The execution completes successfully."

---

## Part 3: One Decision and One Failure (~1.5 minutes)
* **What to show on screen**: Open `crew.py` in your code editor. Highlight the `litellm.completion` monkey-patch (lines 14–32) and the tool isolation lists (lines 68–74).
* **What to say**:
  > "Now, let’s talk about a major technical challenge and a key architectural decision.
  >
  > **The Failure**: Originally, I was using the Gemini API. However, due to quota restrictions and API key authentication conflicts, I pivoted to Groq's `llama-3.1-8b-instant` model. When I did, I hit a critical issue: CrewAI automatically injects Anthropic-style `cache_breakpoint` and `cache_control` headers into its message payloads. Groq's API rejected these parameters and threw validation errors.
  > 
  > To solve this, I wrote a custom monkey-patch on the `litellm.completion` routing system. This wrapper intercepts all outbound API calls and dynamically strips message-level cache headers, allowing the Crew to run flawlessly on Groq.
  >
  > **The Decision**: Another critical choice was tool isolation. In my initial runs, both agents had access to all tools. However, the Writer agent would attempt to run search queries itself when writing the report, passing long descriptive phrases like *'x100 router warranty period and recent issues'* to our keyword matcher, which returned empty results and broke the grounding. 
  > 
  > I made the decision to segregate tools: the Researcher is isolated to `search_documents` and `read_record`, while the Writer is isolated exclusively to the `save_report` tool. This ensures clean delegation of concerns and prevents runaway loops."

---

## Part 4: What You Learned (~1 minute)
* **What to show on screen**: Open `mcp_server.py` in your editor, highlighting the tools (`@mcp.tool()`) and input validations.
* **What to say**:
  > "Building this project taught me a lot about how MCP acts as a standardized interface between LLMs and local infrastructure. Instead of writing custom API wrappers for every agent framework, FastMCP allows us to write standard Python functions that any MCP-compliant agent can inspect and execute.
  > 
  > From a security perspective, a key risk we addressed is path traversal in the `save_report` tool. Since agents receive raw input from files, a malicious document could inject path characters like `../` to overwrite system files. We mitigated this by sanitizing the report title to alphanumeric characters only. We also configured `max_iter=10` on all agents to ensure they fail gracefully rather than looping indefinitely and draining tokens."

---

## Part 5: What is Next (~30 seconds)
* **What to show on screen**: Open `output/Acme_Corp_X100_Report.md` to show the final, beautifully formatted and sourced markdown report.
* **What to say**:
  > "If I were to take this system to production, my next steps would be:
  > 1. Adding a Human-Approval Gate to the `save_report` tool so a human analyst must approve files written to disk.
  > 2. Moving the MCP server from local `stdio` standard streams to a remote `SSE` (Server-Sent Events) network transport.
  > 3. Introducing a Self-Check Agent to cross-validate claims in the report against source files before writing them.
  > 
  > Thank you for watching my demo!"
