import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generators.document_generator import DocumentGenerator

class TestDocumentCleaning(unittest.TestCase):
    def setUp(self):
        self.mock_data_gen = MagicMock()
        self.doc_gen = DocumentGenerator(self.mock_data_gen)

    def test_clean_json_wrapper(self):
        raw_content = '{"content": "# Title\\n\\nThis is the content."}'
        cleaned = self.doc_gen._clean_content(raw_content)
        self.assertEqual(cleaned, "# Title\n\nThis is the content.")

    def test_clean_markdown_block(self):
        raw_content = '```markdown\n# Title\n\nContent\n```'
        cleaned = self.doc_gen._clean_content(raw_content)
        self.assertEqual(cleaned, "# Title\n\nContent")

    def test_clean_json_block(self):
        raw_content = '```json\n{"content": "text"}\n```'
        cleaned = self.doc_gen._clean_content(raw_content)
        self.assertEqual(cleaned, "text")

    def test_clean_plain_text(self):
        raw_content = "# Title\n\nJust text."
        cleaned = self.doc_gen._clean_content(raw_content)
        self.assertEqual(cleaned, "# Title\n\nJust text.")

    def test_clean_prefix(self):
        raw_content = "Here is the document:\n\n# Title\n\nContent"
        cleaned = self.doc_gen._clean_content(raw_content)
        self.assertEqual(cleaned, "# Title\n\nContent")

if __name__ == '__main__':
    unittest.main()
