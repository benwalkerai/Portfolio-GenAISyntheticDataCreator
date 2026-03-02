"""LLM interaction utilities for data generation.

This module handles all LLM interactions including prompting, JSON extraction,
caching, and schema generation.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional


def extract_json(text: str) -> Optional[str]:
    """Extract and validate JSON from LLM response text.
    
    Args:
        text: Raw LLM response text
        
    Returns:
        Valid JSON string or None if extraction fails
    """
    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'(\[.*?\])',
        r'(\{.*?\})'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                candidate = match.group(1).strip()
                json.loads(candidate)
                return candidate
            except:
                continue
    try:
        start_arr, end_arr = text.find('['), text.rfind(']')
        if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
            candidate = text[start_arr:end_arr+1]
            json.loads(candidate)
            return candidate
        start_obj, end_obj = text.find('{'), text.rfind('}')
        if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
            candidate = text[start_obj:end_obj+1]
            json.loads(candidate)
            return candidate
    except:
        pass
    return None


def generate_with_llm(data_generator: Any, llm_cache: Dict[str, str], prompt: str, 
                     cache_key: Optional[str] = None, max_tokens: int = 2500, 
                     json_schema: Optional[Dict] = None) -> str:
    """Generate text using LLM with optional caching.
    
    Args:
        data_generator: The data generator instance with LLM access
        llm_cache: Cache dictionary for storing responses
        prompt: Text prompt for the LLM
        cache_key: Optional cache key for result storage
        max_tokens: Maximum tokens for response
        json_schema: Optional JSON schema for structured output
        
    Returns:
        Generated text response
    """
    if cache_key and cache_key in llm_cache:
        return llm_cache[cache_key]
    try:
        if hasattr(data_generator, 'generate_with_ollama'):
            response = data_generator.generate_with_ollama(prompt, max_tokens=max_tokens, json_schema=json_schema)
        elif hasattr(data_generator, 'generate_with_llm'):
            response = data_generator.generate_with_llm(prompt, max_tokens=max_tokens, json_schema=json_schema)
        elif hasattr(data_generator, 'generate'):
            response = data_generator.generate(prompt, max_tokens=max_tokens)
        elif hasattr(data_generator, 'client') and hasattr(data_generator.client, 'generate'):
            response = data_generator.client.generate(prompt, max_tokens=max_tokens, json_schema=json_schema)
        else:
            print(" No known LLM method on data_generator; returning empty response")
            response = ""
        if cache_key:
            llm_cache[cache_key] = response
        return response
    except Exception as e:
        print(f" LLM generation failed: {e}")
        return ""


def generate_column_headers_with_llm(data_generator: Any, llm_cache: Dict[str, str],
                                    subject: str, num_columns: int,
                                    pad_schema_func, create_fallback_func) -> List[Dict]:
    """Generate column headers and schema using LLM.
    
    Args:
        data_generator: The data generator instance
        llm_cache: Cache dictionary
        subject: Subject/domain for schema
        num_columns: Number of columns to generate
        pad_schema_func: Function to pad schema if needed
        create_fallback_func: Function to create fallback schema
        
    Returns:
        List of column schema dictionaries
    """
    prompt = f"""You are a database schema expert. Generate a realistic schema for "{subject}" with exactly {num_columns} columns.
REQUIREMENTS:
1. Column names must be SHORT and professional (max 3 words)
2. DO NOT use the subject name as a prefix (bad: "employee_name", good: "name" or "full_name")
3. Include diverse data types appropriate for the domain
4. Provide 2-3 realistic examples for categorical fields
5. Add a brief description for each column
Available types: text, number, date, money, percentage, email, phone, id, category, boolean, url, address
OUTPUT FORMAT (valid JSON only):
{{
  "columns": [
    {{
      "name": "column_name",
      "type": "data_type",
      "examples": ["example1", "example2"],
      "description": "what this field represents"
    }}
  ]
}}
Generate {num_columns} columns now:"""
    try:
        print(f" LLM Prompt 1: Generating schema for '{subject}'...")
        response = None
        if hasattr(data_generator, 'client'):
            try:
                json_schema = {
                    "type": "object",
                    "properties": {
                        "columns": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "examples": {"type": "array"},
                                    "description": {"type": "string"}
                                },
                                "required": ["name", "type"]
                            }
                        }
                    },
                    "required": ["columns"]
                }
                response = generate_with_llm(data_generator, llm_cache, prompt, 
                                           cache_key=f"schema_{subject}_{num_columns}", 
                                           json_schema=json_schema)
                print("   Using Ollama structured output")
            except Exception as e:
                print(f"   Structured output failed: {e}")
                response = None
        if response is None:
            response = generate_with_llm(data_generator, llm_cache, prompt, 
                                       cache_key=f"schema_{subject}_{num_columns}")
        cleaned_json = extract_json(response)
        if cleaned_json:
            schema_data = json.loads(cleaned_json)
            if 'columns' in schema_data and isinstance(schema_data['columns'], list):
                columns = schema_data['columns'][:num_columns]
                if len(columns) < num_columns:
                    columns = pad_schema_func(columns, num_columns, subject)
                print(f"   Generated {len(columns)} columns via LLM")
                return columns
        raise ValueError("Invalid JSON schema from LLM")
    except Exception as e:
        print(f"   LLM schema generation failed: {e}")
        print("   Using enhanced template-based schema")
        return create_fallback_func(subject, num_columns)


def generate_domain_constraints_with_llm(data_generator: Any, llm_cache: Dict[str, str],
                                        subject: str, schema: List[Dict]) -> Dict:
    """Generate domain-specific business constraints using LLM.
    
    Args:
        data_generator: The data generator instance
        llm_cache: Cache dictionary
        subject: Subject/domain for constraints
        schema: Schema to analyze for constraints
        
    Returns:
        Dictionary of constraints
    """
    column_summary = ", ".join([f"{col['name']} ({col['type']})" for col in schema[:8]])
    prompt = f"""Analyze this "{subject}" dataset schema and identify realistic business constraints.
Schema: {column_summary}
Generate domain-specific constraints as JSON:
{{
  "correlations": [
    {{
      "field1": "column_name",
      "field2": "column_name", 
      "relationship": "positive/negative/conditional",
      "strength": 0.7,
      "description": "why these correlate"
    }}
  ],
  "value_ranges": [
    {{
      "field": "column_name",
      "min": 10,
      "max": 1000,
      "distribution": "normal/lognormal/uniform/powerlaw",
      "mean": 100,
      "stddev": 20
    }}
  ],
  "temporal_patterns": [
    {{
      "field": "date_column",
      "pattern": "seasonal/cyclical/trending",
      "details": "Q4 has 40% more activity"
    }}
  ],
  "business_rules": [
    "rule description 1",
    "rule description 2"
  ],
  "required_fields": ["field1", "field2"],
  "unique_fields": ["field1"]
}}
Return JSON only:"""
    try:
        print(" LLM Prompt 2: Generating domain constraints...")
        response = generate_with_llm(data_generator, llm_cache, prompt, 
                                   cache_key=f"constraints_{subject}")
        cleaned_json = extract_json(response)
        if cleaned_json:
            constraints = json.loads(cleaned_json)
            print("   Domain constraints generated")
            return constraints
    except Exception as e:
        print(f"   Constraint generation failed: {e}")
    return {
        'correlations': [],
        'value_ranges': [],
        'temporal_patterns': [],
        'business_rules': [],
        'required_fields': [],
        'unique_fields': []
    }


def generate_sample_values_with_llm(data_generator: Any, llm_cache: Dict[str, str],
                                   column_name: str, column_type: str, 
                                   subject: str, count: int = 15) -> List[str]:
    """Generate sample values for a specific column using LLM.
    
    Args:
        data_generator: The data generator instance
        llm_cache: Cache dictionary
        column_name: Name of the column
        column_type: Data type of the column
        subject: Domain/subject context
        count: Number of sample values to generate
        
    Returns:
        List of sample values
    """
    product_context = ""
    if 'product' in subject.lower() and any(kw in column_name.lower() for kw in ['name', 'model', 'sku', 'description']):
        product_context = """
SPECIAL INSTRUCTIONS FOR PRODUCT DATA:
- Generate realistic product names with brand, model, and variant
- Ensure names are unique and commercially viable
- Match naming patterns for the product category
- Include technical specifications where appropriate
"""
    
    prompt = f"""Generate {count} realistic sample values for the column "{column_name}" (type: {column_type}) in a "{subject}" dataset.
{product_context}
Return as a JSON array: ["value1", "value2", ...]
Generate {count} values:"""
    
    try:
        response = generate_with_llm(data_generator, llm_cache, prompt, 
                                   cache_key=f"samples_{subject}_{column_name}_{count}")
        cleaned_json = extract_json(response)
        if cleaned_json:
            values = json.loads(cleaned_json)
            if isinstance(values, list):
                return [str(v) for v in values[:count]]
    except Exception as e:
        print(f"   Sample value generation failed: {e}")
    
    return [f"{column_name}_{i+1}" for i in range(count)]
