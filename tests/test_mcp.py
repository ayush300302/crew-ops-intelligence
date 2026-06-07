import os
import pytest
from mcp_server import search_documents, read_record, save_report, OUTPUT_DIR

def test_search_documents():
    # Test valid query
    result = search_documents("warranty")
    assert "warranty" in result.lower()
    assert "No documents found" not in result
    
    # Test empty query
    result = search_documents("")
    assert "Error: Query cannot be empty" in result
    
    # Test no match
    result = search_documents("unobtanium")
    assert "No documents found" in result

def test_read_record():
    # Test valid record
    result = read_record("R001")
    assert "Acme Corp" in result
    assert "X100 Router" in result
    
    # Test empty record
    result = read_record("")
    assert "Error: record_id cannot be empty" in result
    
    # Test no match
    result = read_record("R999")
    assert "No record found" in result

def test_save_report():
    # Test valid input
    title = "Test_Report"
    content = "# Test\nThis is a test report."
    result = save_report(title, content)
    
    assert "Success" in result
    
    # Verify file was created
    filepath = os.path.join(OUTPUT_DIR, f"{title}.md")
    assert os.path.exists(filepath)
    
    with open(filepath, "r") as f:
        saved_content = f.read()
    assert saved_content == content
    
    # Clean up
    os.remove(filepath)
    
    # Test empty inputs
    result = save_report("", content)
    assert "Error" in result
