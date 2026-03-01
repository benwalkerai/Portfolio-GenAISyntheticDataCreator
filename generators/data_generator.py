from openai import OpenAI
import pandas as pd
from .document_generator import DocumentGenerator
from .excel_generator import ExcelGenerator

class SyntheticDataGenerator:

    def __init__(self, use_llama4=False):
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.use_llama4 = use_llama4
        self.api_base_url = os.getenv('LLM_API_BASE')
        self.api_key = os.getenv('LLM_API_KEY')
        self.model_name = os.getenv('LLM_MODEL')
        if not all([self.api_base_url, self.api_key, self.model_name]):
            print('WARNING: LLM environment variables not fully set. Check .env file.')
            print(f'  LLM_API_BASE: {self.api_base_url}')
            print(f"  LLM_API_KEY: {('*' * 8 if self.api_key else 'Not Set')}")
            print(f'  LLM_MODEL: {self.model_name}')
        print(f'Connecting to LLM at {self.api_base_url} (model: {self.model_name})')
        self.document_generator = DocumentGenerator(self)
        self.excel_generator = ExcelGenerator(self)
        self.client = OpenAI(base_url=self.api_base_url, api_key=self.api_key)

    def generate_with_ollama(self, prompt, max_tokens=None, json_schema=None, system_prompt=None):
        try:
            default_system = 'You are a helpful AI assistant specialized in generating realistic, structured data. Always follow the exact format requested and provide only valid JSON when requested. Focus on creating data that is contextually appropriate and maintains logical relationships between fields.'
            messages = [{'role': 'system', 'content': system_prompt or default_system}, {'role': 'user', 'content': prompt}]
            extra_kwargs = {}
            if json_schema is not None:
                extra_kwargs['response_format'] = {'type': 'json_object'}
            response = self.client.chat.completions.create(model=self.model_name, messages=messages, temperature=0.3, top_p=0.9, max_tokens=max_tokens or 4000, **extra_kwargs)
            return response.choices[0].message.content
        except Exception as e:
            return f'Error: {str(e)}'

    def generate_document(self, content_type, pages, subject, file_format):
        return self.document_generator.generate_document(content_type, pages, subject, file_format)

    def generate_data_file(self, rows, columns, subject, file_format, options=None):
        opts = options or {}
        if 'Excel Spreadsheet (.xlsx)' in file_format:
            opts['format'] = 'xlsx'
        elif 'CSV File (.csv)' in file_format:
            opts['format'] = 'csv'
        temp_path = self.excel_generator.generate_data_file(rows, columns, subject, opts)
        try:
            if 'csv' in opts.get('format', 'xlsx').lower():
                preview_df = pd.read_csv(temp_path, nrows=10)
            else:
                preview_df = pd.read_excel(temp_path, nrows=10)
        except Exception:
            preview_df = pd.DataFrame()
        status_msg = f"Generated {rows} rows x {columns} columns for '{subject}'"
        return (temp_path, status_msg, preview_df)