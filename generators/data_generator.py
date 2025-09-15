"""
Core Synthetic Data Generator Class
Handles Ollama communication and orchestrates document/data generation
"""

import requests
import tempfile
import os
from .document_generator import DocumentGenerator
from .excel_generator import ExcelGenerator


class SyntheticDataGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        #self.ollama_url = "https://llama4.cc-demos.com/v1/chat/completions"
        self.document_generator = DocumentGenerator(self)
        self.excel_generator = ExcelGenerator(self)

    def generate_with_ollama(self, prompt, max_tokens=None):
        """Generate content using local Ollama Mistral Model with enhanced parameters"""
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens or 4000,
                "temperature": 0.7,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }

        try:
            response = requests.post(self.ollama_url, json=payload)
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "Error: Could not connect to Ollama"
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_document(self, content_type, pages, subject, file_format):
        """Generate document content and create file"""
        return self.document_generator.generate_document(content_type, pages, subject, file_format)

    def generate_data_file(self, rows, columns, subject, file_format):
        """Generate Excel/CSV data file"""
        return self.excel_generator.generate_data_file(rows, columns, subject, file_format)
