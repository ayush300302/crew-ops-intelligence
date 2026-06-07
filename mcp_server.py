import os
import csv
import glob
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize FastMCP server
mcp = FastMCP("OperationsAssistant")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "data", "documents")
RECORDS_CSV = os.path.join(BASE_DIR, "data", "records.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

@mcp.tool()
def search_documents(query: str) -> str:
    """
    Search through the operations team's text documents.
    Returns excerpts from documents that match the query.
    """
    if not query:
        return "Error: Query cannot be empty."

    query = query.lower()
    results = []
    
    try:
        doc_files = glob.glob(os.path.join(DOCUMENTS_DIR, "*.txt"))
        for filepath in doc_files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if query in content.lower():
                    filename = os.path.basename(filepath)
                    results.append(f"--- {filename} ---\n{content}\n")
                    
        if not results:
            return f"No documents found matching the query: '{query}'"
            
        return "\n".join(results)
    except Exception as e:
        return f"Error searching documents: {str(e)}"

@mcp.tool()
def read_record(record_id: str) -> str:
    """
    Read a specific record by its ID from the orders/inventory CSV.
    Example record_id: 'R001'
    """
    if not record_id:
        return "Error: record_id cannot be empty."

    try:
        with open(RECORDS_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("record_id") == record_id:
                    # Format as a nice string
                    return "\n".join(f"{k}: {v}" for k, v in row.items())
                    
        return f"No record found with ID: '{record_id}'"
    except Exception as e:
        return f"Error reading record: {str(e)}"

@mcp.tool()
def save_report(title: str, content: str) -> str:
    """
    Save a markdown report to the output folder.
    Returns a success message with the file path.
    """
    if not title or not content:
        return "Error: Both title and content must be provided."

    try:
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Sanitize title for filename
        safe_title = "".join(c if c.isalnum() else "_" for c in title)
        filename = f"{safe_title}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Success! Report saved to {filepath}"
    except Exception as e:
        return f"Error saving report: {str(e)}"

if __name__ == "__main__":
    mcp.run()
