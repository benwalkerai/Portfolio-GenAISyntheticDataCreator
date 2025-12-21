import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generators.document_generator import DocumentGenerator

# Create mock data generator
mock_data_gen = MagicMock()
doc_gen = DocumentGenerator(mock_data_gen)

# Test content with Markdown
test_content = """# Main Heading

This is a paragraph with **bold text** and *italic text* and `code text`.

## Subheading

- Bullet point with **bold**
- Another bullet with *italic*

1. Numbered item one
2. Numbered item two with **formatting**
"""

print("Testing Markdown conversion...")
print("\n=== Original Content ===")
print(test_content)

# Test Word document creation
print("\n=== Creating Word Document ===")
try:
    word_bytes = doc_gen.create_word_document(test_content)
    print(f"✅ Word document created successfully ({len(word_bytes)} bytes)")
    
    # Save to file for manual inspection
    with open("test_output.docx", "wb") as f:
        f.write(word_bytes)
    print("✅ Saved to test_output.docx")
except Exception as e:
    print(f"❌ Error creating Word document: {e}")

# Test PDF document creation
print("\n=== Creating PDF Document ===")
try:
    pdf_bytes = doc_gen.create_pdf_document(test_content)
    print(f"✅ PDF document created successfully ({len(pdf_bytes)} bytes)")
    
    # Save to file for manual inspection
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅ Saved to test_output.pdf")
except Exception as e:
    print(f"❌ Error creating PDF document: {e}")

# Test helper methods
print("\n=== Testing Helper Methods ===")
test_text = "This has **bold** and *italic* and `code`"
stripped = doc_gen._strip_markdown(test_text)
print(f"Stripped: {stripped}")
assert stripped == "This has bold and italic and code", f"Expected plain text, got: {stripped}"
print("✅ _strip_markdown works correctly")

html = doc_gen._markdown_to_html(test_text)
print(f"HTML: {html}")
assert "<b>bold</b>" in html and "<i>italic</i>" in html, f"Expected HTML tags, got: {html}"
print("✅ _markdown_to_html works correctly")

print("\n=== All Tests Passed ===")
print("Please manually inspect test_output.docx and test_output.pdf to verify formatting.")
