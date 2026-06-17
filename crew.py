import os
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# If the user doesn't have a specific API key set, use what's available
load_dotenv()

# Tell litellm to silently drop params that providers don't support
import litellm
import functools
litellm.drop_params = True

# Patch: strip Anthropic-style 'cache_breakpoint' from messages before sending
_original_completion = litellm.completion

@functools.wraps(_original_completion)
def _patched_completion(*args, **kwargs):
    # Remove cache_breakpoint from messages
    messages = kwargs.get("messages", [])
    for msg in messages:
        msg.pop("cache_breakpoint", None)
        msg.pop("cache_control", None)
        # Also check content blocks
        if isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if isinstance(block, dict):
                    block.pop("cache_breakpoint", None)
                    block.pop("cache_control", None)
    return _original_completion(*args, **kwargs)

litellm.completion = _patched_completion

# We will use MCPServerAdapter to expose our FastMCP tools to CrewAI
# According to CrewAI docs for MCP:
# pip install 'crewai[mcp]' or 'crewai-tools[mcp]'
try:
    from crewai_tools import MCPServerAdapter
    from mcp.client.stdio import StdioServerParameters
except ImportError as e:
    print("Failed to import MCP tools. Ensure 'crewai-tools[mcp]' and 'mcp' are installed.")
    raise e

def run_crew():
    # 1. Setup the MCP Server connection via Stdio
    # This tells the MCP client how to start our FastMCP server
    mcp_server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=os.environ.copy()
    )

    # 2. Use MCPServerAdapter as a context manager to ensure proper cleanup
    with MCPServerAdapter(mcp_server_params) as mcp_tools:
        print("Successfully connected to MCP Server!")
        
        # Configure LLM - Using Groq (free tier, generous rate limits)
        groq_api_key = os.environ.get("GROQ_API_KEY", "")
        if not groq_api_key:
            print("ERROR: GROQ_API_KEY not found in .env file!")
            return

        llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=groq_api_key,
            temperature=0.7
        )
        print(f"Using LLM: groq/llama-3.1-8b-instant")

        # Define Agents
        researcher = Agent(
            role="Operations Researcher",
            goal="Find relevant documents and records to answer business questions accurately.",
            backstory="You are an expert operations analyst who can quickly search through policies, support tickets, and inventory records to find facts.",
            tools=mcp_tools,
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=10 # Loop control to prevent runaway agents
        )

        writer = Agent(
            role="Operations Report Writer",
            goal="Synthesize research findings into clear, sourced markdown reports.",
            backstory="You are a meticulous technical writer. You only state facts that are backed by retrieved documents or records, and you always cite your sources.",
            tools=mcp_tools,
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=10
        )

        # Define Tasks
        question = "What is the warranty period for the X100 Router, and what was the resolution for the recent support ticket from Acme Corp regarding this router?"
        
        research_task = Task(
            description=f"""
            Research the following question using your tools:
            "{question}"
            
            IMPORTANT INSTRUCTIONS FOR USING TOOLS:
            - The search_documents tool does simple keyword matching. Use SHORT, SINGLE-WORD queries.
            - For example, search for "warranty" (not "warranty period for X100 Router").
            - Search for "acme" to find Acme Corp tickets (not "support ticket from Acme Corp").
            - Search for "x100" to find X100 Router info.
            - Use read_record with record IDs like "R001" to look up inventory records.
            
            Steps:
            1. Search documents with query "warranty" to find the warranty period.
            2. Search documents with query "acme" to find the support ticket from Acme Corp.
            3. Use read_record with "R001" to check Acme Corp's inventory record.
            
            Return a summary of ALL the facts you found, including the exact document names or record IDs where you found them.
            """,
            expected_output="A detailed summary of facts with explicit citations to the document names or record IDs.",
            agent=researcher
        )

        report_task = Task(
            description="""
            Using the facts provided by the researcher, write a short, clear markdown report answering the user's question.
            
            CRITICAL RULES:
            - Every claim MUST cite the document or record it came from.
            - If no evidence is found for a part of the question, state that clearly instead of inventing an answer.
            - Once the report is written, use the `save_report` tool to save it with the title "Acme_Corp_X100_Report".
            """,
            expected_output="A confirmation message that the report was successfully saved using the save_report tool.",
            agent=writer
        )

        # Form the Crew
        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, report_task],
            process=Process.sequential,
            verbose=True
        )

        # Execute
        print("Starting Crew execution...")
        result = crew.kickoff()
        print("\n=== CREW EXECUTION COMPLETED ===")
        print(result)

if __name__ == "__main__":
    run_crew()
