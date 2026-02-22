"""Main orchestrator for data and document generation."""

from typing import Optional, Dict, Any, Tuple
from openai import OpenAI
import pandas as pd
from .document_generator import DocumentGenerator
from .excel_generator import ExcelGenerator


class SyntheticDataGenerator:
    """Coordinate document and tabular data generation via the LLM client."""
    
    def __init__(self, use_llama4: bool = False) -> None:
        """
        Initialize the synthetic data generator with LLM configuration.
        
        Args:
            use_llama4 (bool): Deprecated. Configuration is now loaded from environment variables.
        """
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        self.use_llama4 = use_llama4
        
        # Load configuration from environment variables
        self.api_base_url = os.getenv("LLM_API_BASE")
        self.api_key = os.getenv("LLM_API_KEY")
        self.model_name = os.getenv("LLM_MODEL")
        
        if not all([self.api_base_url, self.api_key, self.model_name]):
            print("[WARNING] LLM environment variables not fully set. Please check your .env file.")
            print(f"  LLM_API_BASE: {self.api_base_url}")
            print(f"  LLM_API_KEY: {'*' * 8 if self.api_key else 'Not Set'}")
            print(f"  LLM_MODEL: {self.model_name}")
        
        print(f"[INFO] Connecting to Local LLM at {self.api_base_url} with model {self.model_name}")
        
        # Initialize specialized generators
        self.document_generator = DocumentGenerator(self)
        self.excel_generator = ExcelGenerator(self)
        
        # Create OpenAI client for API calls
        self.client = OpenAI(
            base_url=self.api_base_url,
            api_key=self.api_key,
        )
    
    def generate_with_ollama(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None, 
        json_schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate content via LLM API (Ollama or llama4.cc-demos.com).
        
        This method handles all LLM communication with enhanced prompting for
        structured data generation. It supports both regular text generation
        and structured JSON output when a schema is provided.
        
        Args:
            prompt (str): The user prompt to send to the LLM
            max_tokens (Optional[int]): Maximum tokens to generate. Defaults to 4000.
            json_schema (Optional[Dict[str, Any]]): JSON schema for structured output.
                                                  If provided, forces JSON response format.
            system_prompt (Optional[str]): Custom system prompt to override the default.
        
        Returns:
            str: Generated content from the LLM, or error message if generation fails.
        
        Example:
            >>> generator = SyntheticDataGenerator()
            >>> response = generator.generate_with_ollama(
            ...     "Generate 5 product names for electronics",
            ...     max_tokens=200
            ... )
            >>> print(response)
            "1. Quantum Headphones Pro\\n2. Smart Wireless Charger..."
        
        Note:
            - Uses temperature=0.3 for consistent structured output
            - Automatically handles JSON schema enforcement when provided
            - Includes enhanced system prompt for better data generation
        """
        try:
            # Enhanced system prompt for better structured data generation
            default_system = "You are a helpful AI assistant specialized in generating realistic, structured data. Always follow the exact format requested and provide only valid JSON when requested. Focus on creating data that is contextually appropriate and maintains logical relationships between fields."
            
            messages = [
                {
                    "role": "system", 
                    "content": system_prompt or default_system
                },
                {"role": "user", "content": prompt}
            ]

            # Prepare additional parameters for API call
            extra_kwargs = {}
            if json_schema is not None:
                # For models that support structured output (like some Ollama models with format='json')
                extra_kwargs['response_format'] = {"type": "json_object"}
            
            # Make API call with optimized parameters
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent structured output
                top_p=0.9,
                max_tokens=max_tokens or 4000,
                **extra_kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_document(
        self, 
        content_type: str, 
        pages: int, 
        subject: str, 
        file_format: str
    ) -> Tuple[str, str, Any]:
        """
        Generate document content and create file using the document generator.
        
        This method delegates to the specialized document generator to create
        various document formats including Word, PDF, and text files.
        
        Args:
            content_type (str): Type of document to generate (e.g., "article", "report")
            pages (int): Number of pages to generate
            subject (str): Subject/topic for the document content
            file_format (str): Output format ("Word Document (.docx)", "PDF Document (.pdf)", "Text File (.txt)")
        
        Returns:
            Tuple[str, str, Any]: (file_path, status_message, preview_data)
        
        Example:
            >>> generator = SyntheticDataGenerator()
            >>> path, status, preview = generator.generate_document(
            ...     "article", 5, "AI Governance", "Word Document (.docx)"
            ... )
            >>> print(f"Generated: {path}")
        """
        return self.document_generator.generate_document(content_type, pages, subject, file_format)
    
    def generate_data_file(
        self, 
        rows: int, 
        columns: int, 
        subject: str, 
        file_format: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, Any]:
        """
        Generate Excel/CSV data file with options for realism controls.
        
        This method delegates to the specialized Excel generator to create
        structured data files with advanced realism features including
        correlations, distributions, and data quality controls.
        
        Args:
            rows (int): Number of rows to generate
            columns (int): Number of columns to generate
            subject (str): Subject/domain for data generation (e.g., "Product Catalogue")
            file_format (str): Output format ("Excel Spreadsheet (.xlsx)", "CSV File (.csv)")
            options (Optional[Dict[str, Any]]): Additional options for data generation:
                - enforce_correlations (bool): Enable cross-field correlations
                - prevent_future (bool): Prevent future dates
                - apply_distributions (bool): Use statistical distributions
                - add_missingness (bool): Introduce missing values
                - missingness_rate (float): Rate of missing values (0.0-0.3)
                - add_noise (bool): Add realistic noise/typos
                - noise_level (float): Level of noise (0.0-0.2)
        
        Returns:
            Tuple[str, str, Any]: (file_path, status_message, preview_dataframe)
        
        Example:
            >>> generator = SyntheticDataGenerator()
            >>> path, status, preview = generator.generate_data_file(
            ...     1000, 10, "Employee Information", "Excel Spreadsheet (.xlsx)",
            ...     {"enforce_correlations": True, "add_missingness": True}
            ... )
            >>> print(f"Generated: {path}")
        """
        # Convert file_format string to format in options dict
        opts = options or {}
        if "Excel Spreadsheet (.xlsx)" in file_format:
            opts['format'] = 'xlsx'
        elif "CSV File (.csv)" in file_format:
            opts['format'] = 'csv'
        
        # Call excel generator
        temp_path = self.excel_generator.generate_data_file(rows, columns, subject, opts)
        
        # Generate preview (first 10 rows)
        try:
            if 'csv' in opts.get('format', 'xlsx').lower():
                preview_df = pd.read_csv(temp_path, nrows=10)
            else:
                preview_df = pd.read_excel(temp_path, nrows=10)
        except Exception:
            preview_df = pd.DataFrame()
        
        status_msg = f"✅ Generated {rows} rows × {columns} columns for '{subject}' successfully!"
        return temp_path, status_msg, preview_df