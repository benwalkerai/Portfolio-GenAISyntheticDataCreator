import os
import sys
import re
import json
import random
import traceback
import tempfile
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from utils.product_constraints import ProductConstraints
except ImportError:
    print("ProductConstraints not found, using built-in constraints")
    ProductConstraints = None
class ExcelGenerator:
    _PRODUCT_NAMES = {
        'Electronics': {
            'items': [
                ('Quantum', 'Display', ['4K', '8K', 'QLED', 'MicroLED'], (799.99, 3499.99)),
                ('Acoustic', 'Headphones', ['Pro', 'Air', 'Go', 'Studio'], (99.99, 399.99)),
                ('Volt', 'Charger', ['Max', 'Mini', 'Duo', 'Ultra'], (29.99, 79.99)),
                ('Connect', 'Router', ['AX3000', 'AX6000', 'AX11000'], (129.99, 399.99)),
                ('Pixel', 'Camera', ['24MP', '48MP', '64MP'], (599.99, 2499.99))
            ],
            'stock_p': 0.05,
            'prefix': 'ELEC',
            'lifecycle_months': (6, 36),
            'seasonality': {'Q4': 1.4, 'Q1': 0.8, 'Q2': 1.0, 'Q3': 1.1}
        },
        'Apparel': {
            'items': [
                ('Trek', 'Jacket', ['Waterproof', 'Insulated', 'Lite', 'Winter'], (89.99, 299.99)),
                ('Urban', 'Jeans', ['Slim', 'Relaxed', 'Classic', 'Skinny'], (59.99, 129.99)),
                ('Active', 'T-Shirt', ['Dry-Fit', 'Cotton', 'Performance'], (19.99, 49.99)),
                ('Sport', 'Sneakers', ['Running', 'Training', 'Casual'], (79.99, 189.99))
            ],
            'stock_p': 0.02,
            'prefix': 'APRL',
            'lifecycle_months': (3, 18),
            'seasonality': {'Q4': 1.3, 'Q1': 0.9, 'Q2': 1.0, 'Q3': 1.2}
        },
        'Home Goods': {
            'items': [
                ('Aero', 'Coffee Maker', ['Press', 'Drip', 'Express', 'Pod'], (24.99, 199.99)),
                ('Cozy', 'Blanket', ['Plush', 'Woven', 'Heated', 'Fleece'], (39.99, 149.99)),
                ('Chef', 'Knife Set', ['Pro', 'Essential', 'Master'], (79.99, 499.99)),
                ('Smart', 'Thermostat', ['Basic', 'Pro', 'Elite'], (129.99, 299.99))
            ],
            'stock_p': 0.03,
            'prefix': 'HOME',
            'lifecycle_months': (12, 60),
            'seasonality': {'Q4': 1.5, 'Q1': 0.8, 'Q2': 0.9, 'Q3': 1.0}
        },
        'Outdoor Gear': {
            'items': [
                ('Summit', 'Backpack', ['50L', '70L', '90L'], (149.99, 349.99)),
                ('Trail', 'Tent', ['2-Person', '4-Person', '6-Person'], (199.99, 499.99)),
                ('Blaze', 'Headlamp', ['500', '750', '1000'], (49.99, 99.99)),
                ('Alpine', 'Sleeping Bag', ['0°F', '15°F', '30°F'], (89.99, 249.99))
            ],
            'stock_p': 0.08,
            'prefix': 'OUTD',
            'lifecycle_months': (18, 72),
            'seasonality': {'Q4': 0.9, 'Q1': 0.8, 'Q2': 1.3, 'Q3': 1.4}
        },
        'Automotive': {
            'items': [
                ('All-Terrain', 'Tire Set', ['265/70R17', '285/75R16', '275/65R18'], (800.00, 1600.00)),
                ('Synthetic', 'Motor Oil', ['5W-30', '10W-40', '0W-20'], (35.00, 65.00)),
                ('Hydro', 'Wiper Blade', ['22-inch', '26-inch', '28-inch'], (15.00, 30.00)),
                ('Premium', 'Air Filter', ['Standard', 'Performance', 'HEPA'], (19.99, 59.99))
            ],
            'stock_p': 0.01,
            'prefix': 'AUTO',
            'lifecycle_months': (24, 84),
            'seasonality': {'Q4': 1.0, 'Q1': 1.1, 'Q2': 1.0, 'Q3': 0.9}
        }
    }
    _LOCATIONS = {
        'USA': {
            'states': ['CA', 'NY', 'TX', 'FL', 'IL', 'WA', 'MA', 'CO', 'GA', 'NC'],
            'cities': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Seattle', 
                      'Austin', 'Dallas', 'Boston', 'Denver'],
            'currency': 'USD',
            'currency_symbol': '$',
            'salary_multiplier': 1.0,
            'phone_format': 'US',
            'decimal_separator': '.',
            'region_multipliers': {'CA': 1.25, 'NY': 1.20, 'TX': 0.95, 'FL': 0.98}
        },
        'Canada': {
            'states': ['ON', 'QC', 'BC', 'AB', 'SK', 'MB'],
            'cities': ['Toronto', 'Montreal', 'Vancouver', 'Calgary', 'Edmonton', 'Ottawa', 'Winnipeg'],
            'currency': 'CAD',
            'currency_symbol': 'C$',
            'salary_multiplier': 0.88,
            'phone_format': 'CA',
            'decimal_separator': '.'
        },
        'UK': {
            'states': ['England', 'Scotland', 'Wales', 'N. Ireland'],
            'cities': ['London', 'Birmingham', 'Glasgow', 'Liverpool', 'Bristol', 'Manchester', 'Edinburgh'],
            'currency': 'GBP',
            'currency_symbol': '£',
            'salary_multiplier': 0.95,
            'phone_format': 'UK',
            'decimal_separator': '.'
        },
        'Germany': {
            'states': ['BW', 'BY', 'BE', 'HE', 'NRW'],
            'cities': ['Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt', 'Stuttgart', 'Dusseldorf'],
            'currency': 'EUR',
            'currency_symbol': '€',
            'salary_multiplier': 0.92,
            'phone_format': 'DE',
            'decimal_separator': ','
        },
        'Australia': {
            'states': ['NSW', 'VIC', 'QLD', 'WA', 'SA'],
            'cities': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Gold Coast'],
            'currency': 'AUD',
            'currency_symbol': 'A$',
            'salary_multiplier': 0.93,
            'phone_format': 'AU',
            'decimal_separator': '.'
        },
        'Japan': {
            'states': ['Tokyo', 'Kanagawa', 'Osaka', 'Aichi', 'Hokkaido'],
            'cities': ['Tokyo', 'Yokohama', 'Osaka', 'Nagoya', 'Sapporo', 'Fukuoka', 'Kobe'],
            'currency': 'JPY',
            'currency_symbol': '¥',
            'salary_multiplier': 0.85,
            'phone_format': 'JP',
            'decimal_separator': '.'
        },
        'India': {
            'states': ['MH', 'DL', 'KA', 'TN', 'WB'],
            'cities': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune'],
            'currency': 'INR',
            'currency_symbol': '₹',
            'salary_multiplier': 0.35,
            'phone_format': 'IN',
            'decimal_separator': '.'
        }
    }
    LOCATIONS_ALIASES = {
        'Usa': 'USA',
        'usa': 'USA', 
        'Uk': 'UK',
        'uk': 'UK',
        'Hr': 'HR',
        'hr': 'HR',
        'It': 'IT',
        'it': 'IT'
}
    _INTERNATIONAL_NAMES = {
        'Anglo': {
            'first': ['John', 'Jane', 'Michael', 'Emily', 'David', 'Laura', 'Robert', 'Sarah'],
            'last': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller']
        },
        'East Asian': {
            'first': ['Ken', 'Yuki', 'Hiro', 'Yuna', 'Li', 'Wei'],
            'last': ['Wang', 'Li', 'Suzuki', 'Kim', 'Chen']
        },
        'South Asian': {
            'first': ['Amit', 'Priya', 'Ravi', 'Sana', 'Vikram'],
            'last': ['Patel', 'Singh', 'Kumar', 'Shah']
        },
        'European': {
            'first': ['Luca', 'Sofia', 'Hans', 'Marie', 'Franco'],
            'last': ['Muller', 'Garcia', 'Rossi', 'Weber']
        }
    }
    _INDUSTRY_KEYWORDS = {
        'generic': ['Solutions', 'Systems', 'Services', 'Works'],
        'tech': ['Technologies', 'Labs', 'Systems', 'Soft'],
        'finance': ['Capital', 'Investments', 'Holdings'],
        'manufacturing': ['Manufacturing', 'Industries', 'Supply'],
        'healthcare': ['Health', 'Medical', 'Care']
    }
    _DOMAINS = ['example.com', 'company.com', 'corporate.com']
    _STREET_NAMES = ['Maple', 'Oak', 'Pine', 'Cedar', 'Elm', 'Washington', 'Main', 'Park', 
                    'Sunset', 'River', 'Lake', 'Hill', 'Valley', 'Forest', 'Meadow', 'Spring',
                    'Grove', 'Ridge', 'Bay', 'Shore']
    _STREET_TYPES = ['St', 'Ave', 'Blvd', 'Rd', 'Ln', 'Dr', 'Ct', 'Way', 'Pl', 'Ter', 'Cir']
    def __init__(self, data_generator: Any) :
        self.data_generator = data_generator
        self.llm_cache = {}
        self.domain_constraints = {}
        self._active_generation_options = {}
    def clear_cache(self) :
        self.llm_cache.clear()
        if hasattr(self, 'country_city_cache'):
            self.country_city_cache.clear()
        print("ExcelGenerator cache cleared")
    def get_country_cities_from_llm(self, countries: List[str]) :
        import json
        if not hasattr(self, '_country_city_cache'):
            self._country_city_cache = {}
        uncached_countries = [c for c in countries if c not in self._country_city_cache]
        if not uncached_countries:
            return self._country_city_cache
        KNOWN_CITIES = {
            'USA': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'],
            'Usa': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'],
            'UK': ['London', 'Manchester', 'Birmingham', 'Leeds', 'Liverpool', 'Bristol'],
            'Uk': ['London', 'Manchester', 'Birmingham', 'Leeds', 'Liverpool', 'Bristol'],
            'Canada': ['Toronto', 'Montreal', 'Vancouver', 'Calgary', 'Edmonton', 'Ottawa'],
            'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Gold Coast'],
            'Japan': ['Tokyo', 'Osaka', 'Yokohama', 'Nagoya', 'Sapporo', 'Kobe'],
            'Germany': ['Berlin', 'Munich', 'Frankfurt', 'Hamburg', 'Cologne', 'Stuttgart'],
            'India': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata']
        }
        known_count = 0
        unknown = []
        for country in uncached_countries:
            if country in KNOWN_CITIES:
                self._country_city_cache[country] = KNOWN_CITIES[country]
                known_count += 1
            else:
                unknown.append(country)
        if known_count > 0:
            print(f"Used real cities for {known_count} known countries")
        if unknown:
            print(f"Generating cities for {len(unknown)} unknown countries")
            countries_str = ', '.join(unknown)
            prompt = f"""List 6 major cities for each country. Return ONLY valid JSON.
    Countries: {countries_str}
    Format (exact):
    {{"CountryName": ["City1", "City2", "City3", "City4", "City5", "City6"]}}
    JSON only, no explanation:"""
            try:
                response = self.data_generator.generate_with_ollama(prompt, max_tokens=800)
                cleaned = response.strip()
                if cleaned.startswith('```'):
                    cleaned = re.sub(r'^```(json)?\s*', '', cleaned)
                    cleaned = re.sub(r'```\s*$', '', cleaned)
                if '{' in cleaned and '}' in cleaned:
                    start = cleaned.index('{')
                    end = cleaned.rindex('}') + 1
                    json_str = cleaned[start:end]
                    cities_data = json.loads(json_str)
                    for country, cities in cities_data.items():
                        if isinstance(cities, list) and len(cities) > 0:
                            self._country_city_cache[country] = cities
                    print(f"Generated cities for {len(cities_data)} countries")
                else:
                    print(f"No JSON found in response")
            except Exception as e:
                print(f"City generation error: {e}")
                for country in unknown:
                    self._country_city_cache[country] = ['Capital City', 'Major City', 'Port City', 'Urban Center', 'Regional Hub', 'Metro Area']
        return self._country_city_cache
    def apply_country_city_fix(self, df: pd.DataFrame) :
        if 'Country' not in df.columns or 'City' not in df.columns:
            return df
        unique_countries = df['Country'].dropna().unique().tolist()
        if not unique_countries:
            return df
        COUNTRY_CITIES = self.get_country_cities_from_llm(unique_countries)
        fixes = 0
        for idx in range(len(df)):
            country = df.at[idx, 'Country']
            city = df.at[idx, 'City']
            if pd.notna(country) and pd.notna(city):
                valid_cities = COUNTRY_CITIES.get(country, [])
                if len(valid_cities) > 0 and city not in valid_cities:
                    df.at[idx, 'City'] = random.choice(valid_cities)
                    fixes += 1
        if fixes > 0:
            print(f"   Fixed {fixes} country-city mismatches with real cities")
        return df
    def extract_json(self, text: str) :
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
    def generate_with_llm(self, prompt = None, 
                         max_tokens = 2500, json_schema: Optional[Dict] = None) -> str:
        if cache_key and cache_key in self.llm_cache:
            return self.llm_cache[cache_key]
        try:
            if hasattr(self.data_generator, 'generate_with_ollama'):
                response = self.data_generator.generate_with_ollama(prompt, max_tokens=max_tokens, json_schema=json_schema)
            elif hasattr(self.data_generator, 'generate_with_llm'):
                response = self.data_generator.generate_with_llm(prompt, max_tokens=max_tokens, json_schema=json_schema)
            elif hasattr(self.data_generator, 'generate'):
                response = self.data_generator.generate(prompt, max_tokens=max_tokens)
            elif hasattr(self.data_generator, 'client') and hasattr(self.data_generator.client, 'generate'):
                response = self.data_generator.client.generate(prompt, max_tokens=max_tokens, json_schema=json_schema)
            else:
                print(" No known LLM method on data_generator; returning empty response")
                response = ""
            if cache_key:
                self.llm_cache[cache_key] = response
            return response
        except Exception as e:
            print(f" LLM generation failed: {e}")
            return ""
    def generate_column_headers_with_llm(self, subject: str, num_columns: int) :
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
            if hasattr(self.data_generator, 'client'):
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
                    response = self.generate_with_llm(prompt, cache_key=f"schema_{subject}_{num_columns}", json_schema=json_schema)
                    print("   Using Ollama structured output")
                except Exception as e:
                    print(f"   Structured output failed: {e}")
                    response = None
            if response is None:
                response = self.generate_with_llm(prompt, cache_key=f"schema_{subject}_{num_columns}")
            cleaned_json = self.extract_json(response)
            if cleaned_json:
                schema_data = json.loads(cleaned_json)
                if 'columns' in schema_data and isinstance(schema_data['columns'], list):
                    columns = schema_data['columns'][:num_columns]
                    if len(columns) < num_columns:
                        columns = self._pad_schema(columns, num_columns, subject)
                    print(f"   Generated {len(columns)} columns via LLM")
                    return columns
            raise ValueError("Invalid JSON schema from LLM")
        except Exception as e:
            print(f"   LLM schema generation failed: {e}")
            print("   Using enhanced template-based schema")
            return self.create_enhanced_fallback_schema(subject, num_columns)
    def generate_domain_constraints_with_llm(self, subject: str, schema: List[Dict]) :
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
            response = self.generate_with_llm(prompt, cache_key=f"constraints_{subject}")
            cleaned_json = self.extract_json(response)
            if cleaned_json:
                constraints = json.loads(cleaned_json)
                self.domain_constraints = constraints
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
    def generate_sample_values_with_llm(self, column_name: str, column_type: str, 
                                   subject = 15) -> List[str]:
        product_context = ""
        if 'product' in subject.lower() and any(kw in column_name.lower() for kw in ['name', 'model', 'sku', 'description']):
            product_context = """
SPECIAL INSTRUCTIONS FOR PRODUCT DATA:
- Generate realistic product names with brand, model, and variant
- Ensure names are unique and commercially viable
- Match naming patterns for the product category
- Include technical specifications where appropriate
        ENHANCED: LLM Prompt 4 - Validate generated data quality.
        Final check to ensure data looks realistic.
        print(f" Creating fallback schema for '{subject}'")
        base_schemas = {
            'employee': [
                {"name": "EmployeeID", "type": "id", "examples": ["EMP-10234"], "description": "Unique employee identifier"},
                {"name": "FirstName", "type": "text", "examples": ["John", "Maria"], "description": "Employee first name"},
                {"name": "LastName", "type": "text", "examples": ["Smith", "Garcia"], "description": "Employee last name"},
                {"name": "Email", "type": "email", "examples": ["john.smith@company.com"], "description": "Work email"},
                {"name": "Department", "type": "category", "examples": ["IT", "Finance", "HR", "Marketing"], "description": "Department"},
                {"name": "JobTitle", "type": "text", "examples": ["Software Engineer", "Manager"], "description": "Job position"},
                {"name": "Manager", "type": "text", "examples": ["Jane Doe"], "description": "Reports to"},
                {"name": "HireDate", "type": "date", "examples": ["2020-03-15"], "description": "Date hired"},
                {"name": "Salary", "type": "money", "examples": ["65000"], "description": "Annual salary"},
                {"name": "PhoneNumber", "type": "phone", "examples": ["555-123-4567"], "description": "Contact phone"},
                {"name": "Country", "type": "category", "examples": list(self._LOCATIONS.keys()), "description": "Work location"},
                {"name": "City", "type": "text", "examples": ["New York"], "description": "City"},
                {"name": "Status", "type": "category", "examples": ["Active", "On Leave"], "description": "Employment status"}
            ],
            'sales': [
                {"name": "OrderID", "type": "id", "examples": ["ORD-50123"], "description": "Order number"},
                {"name": "OrderDate", "type": "date", "examples": ["2025-01-15"], "description": "Date ordered"},
                {"name": "CustomerID", "type": "id", "examples": ["CUST-1234"], "description": "Customer ID"},
                {"name": "CustomerName", "type": "text", "examples": ["Acme Corp"], "description": "Customer"},
                {"name": "ProductSKU", "type": "id", "examples": ["ELEC-QU4K-1234"], "description": "Product SKU"},
                {"name": "ProductName", "type": "text", "examples": ["Quantum 4K Display"], "description": "Product"},
                {"name": "Category", "type": "category", "examples": list(self._PRODUCT_NAMES.keys()), "description": "Product category"},
                {"name": "Quantity", "type": "number", "examples": ["1", "5"], "description": "Quantity sold"},
                {"name": "UnitPrice", "type": "money", "examples": ["99.99"], "description": "Price per unit"},
                {"name": "TotalSale", "type": "money", "examples": ["499.95"], "description": "Total amount"},
                {"name": "SalesRep", "type": "text", "examples": ["John Smith"], "description": "Sales representative"},
                {"name": "Region", "type": "category", "examples": ["North", "South", "East", "West"], "description": "Sales region"},
                {"name": "Status", "type": "category", "examples": ["Completed", "Pending"], "description": "Order status"}
            ],
            'product': [
                {"name": "ProductID", "type": "id", "examples": ["PROD-1001"], "description": "Product ID"},
                {"name": "ProductName", "type": "text", "examples": ["Quantum 4K Display"], "description": "Product name"},
                {"name": "SKU", "type": "id", "examples": ["ELEC-QU4K-1234"], "description": "Stock keeping unit"},
                {"name": "Category", "type": "category", "examples": list(self._PRODUCT_NAMES.keys()), "description": "Category"},
                {"name": "Price", "type": "money", "examples": ["299.99"], "description": "Retail price"},
                {"name": "Cost", "type": "money", "examples": ["150.00"], "description": "Cost basis"},
                {"name": "StockQuantity", "type": "number", "examples": ["50"], "description": "Current stock"},
                {"name": "ReorderLevel", "type": "number", "examples": ["10"], "description": "Reorder threshold"},
                {"name": "Supplier", "type": "text", "examples": ["Global Manufacturing"], "description": "Supplier name"},
                {"name": "DateAdded", "type": "date", "examples": ["2023-06-15"], "description": "Added to catalog"}
            ],
            'customer': [
                {"name": "CustomerID", "type": "id", "examples": ["CUST-5001"], "description": "Unique customer identifier"},
                {"name": "CompanyName", "type": "text", "examples": ["Acme Corporation", "Global Industries"], "description": "Company name"},
                {"name": "Industry", "type": "category", "examples": ["Technology", "Manufacturing", "Retail", "Healthcare", "Finance"], "description": "Industry sector"},
                {"name": "ContactPerson", "type": "text", "examples": ["John Smith", "Maria Garcia"], "description": "Primary contact"},
                {"name": "Email", "type": "email", "examples": ["contact@acme.com"], "description": "Contact email"},
                {"name": "PhoneNumber", "type": "phone", "examples": ["555-123-4567"], "description": "Contact phone"},
                {"name": "Country", "type": "category", "examples": list(self._LOCATIONS.keys()), "description": "Country"},
                {"name": "City", "type": "text", "examples": ["New York"], "description": "City"},
                {"name": "AccountStatus", "type": "category", "examples": ["Active", "Inactive", "Pending"], "description": "Account status"},
                {"name": "CreditLimit", "type": "money", "examples": ["50000"], "description": "Credit limit"},
                {"name": "JoinDate", "type": "date", "examples": ["2020-03-15"], "description": "Customer since"},
                {"name": "LastOrderDate", "type": "date", "examples": ["2024-12-01"], "description": "Last order date"}
            ],
            'supplier': [
                {"name": "SupplierID", "type": "id", "examples": ["SUP-3001"], "description": "Unique supplier identifier"},
                {"name": "CompanyName", "type": "text", "examples": ["Global Manufacturing", "Tech Supplies Inc"], "description": "Supplier company name"},
                {"name": "Industry", "type": "category", "examples": ["Manufacturing", "Distribution", "Technology", "Raw Materials"], "description": "Industry sector"},
                {"name": "ContactPerson", "type": "text", "examples": ["Jane Doe", "Carlos Martinez"], "description": "Primary contact"},
                {"name": "Email", "type": "email", "examples": ["sales@supplier.com"], "description": "Contact email"},
                {"name": "PhoneNumber", "type": "phone", "examples": ["555-987-6543"], "description": "Contact phone"},
                {"name": "PaymentTerms", "type": "category", "examples": ["Net 30", "Net 60", "Net 90", "COD", "Prepaid"], "description": "Payment terms"},
                {"name": "MinimumOrder", "type": "money", "examples": ["1000", "5000"], "description": "Minimum order amount"},
                {"name": "LeadTime", "type": "number", "examples": ["7", "14", "30"], "description": "Lead time in days"},
                {"name": "Country", "type": "category", "examples": list(self._LOCATIONS.keys()), "description": "Country"},
                {"name": "City", "type": "text", "examples": ["Shanghai"], "description": "City"},
                {"name": "Status", "type": "category", "examples": ["Active", "Inactive", "Pending"], "description": "Supplier status"}
            ],
            'support': [
                {"name": "TicketID", "type": "id", "examples": ["TKT-10234"], "description": "Ticket number"},
                {"name": "DateCreated", "type": "date", "examples": ["2025-08-15"], "description": "Created date"},
                {"name": "CustomerName", "type": "text", "examples": ["John Smith"], "description": "Customer"},
                {"name": "Email", "type": "email", "examples": ["john@example.com"], "description": "Contact email"},
                {"name": "Priority", "type": "category", "examples": ["Low", "Medium", "High", "Critical"], "description": "Priority level"},
                {"name": "Status", "type": "category", "examples": ["Open", "In Progress", "Resolved"], "description": "Ticket status"},
                {"name": "AssignedTo", "type": "text", "examples": ["Support Agent 1"], "description": "Assigned agent"},
                {"name": "Category", "type": "category", "examples": ["Technical", "Billing", "General"], "description": "Issue category"},
                {"name": "Subject", "type": "text", "examples": ["Login issue"], "description": "Issue summary"},
                {"name": "Resolution", "type": "text", "examples": ["Password reset sent"], "description": "Resolution details"}
            ],
            'financial': [
                {"name": "TransactionID", "type": "id", "examples": ["TXN-89234567"], "description": "Unique transaction identifier"},
                {"name": "AccountNumber", "type": "id", "examples": ["ACC-123456789"], "description": "Account number"},
                {"name": "TransactionDate", "type": "date", "examples": ["2025-01-15"], "description": "Transaction date"},
                {"name": "PostedDate", "type": "date", "examples": ["2025-01-16"], "description": "Posted date"},
                {"name": "TransactionType", "type": "category", "examples": ["Debit", "Credit", "Transfer", "Payment", "Withdrawal", "Deposit"], "description": "Transaction type"},
                {"name": "Amount", "type": "money", "examples": ["1234.56"], "description": "Transaction amount"},
                {"name": "Currency", "type": "category", "examples": ["USD", "EUR", "GBP", "JPY", "CAD"], "description": "Currency"},
                {"name": "Balance", "type": "money", "examples": ["45678.90"], "description": "Account balance after transaction"},
                {"name": "MerchantName", "type": "text", "examples": ["Amazon", "Walmart", "Shell Gas Station"], "description": "Merchant or payee"},
                {"name": "Category", "type": "category", "examples": ["Groceries", "Utilities", "Entertainment", "Travel", "Healthcare", "Shopping"], "description": "Transaction category"},
                {"name": "PaymentMethod", "type": "category", "examples": ["Card", "ACH", "Wire", "Check", "Cash"], "description": "Payment method"},
                {"name": "Status", "type": "category", "examples": ["Posted", "Pending", "Cleared", "Failed"], "description": "Transaction status"},
                {"name": "Description", "type": "text", "examples": ["Purchase at store", "Monthly payment"], "description": "Transaction description"},
                {"name": "AuthCode", "type": "id", "examples": ["AUTH-ABC123"], "description": "Authorization code"},
                {"name": "Notes", "type": "text", "examples": ["", "Recurring monthly"], "description": "Additional notes"}
            ]
        }
        subject_lower = subject.lower()
        key = 'employee'
        if 'financial' in subject_lower and 'transaction' in subject_lower:
            key = 'financial'
        elif any(s in subject_lower for s in ['customer', 'client', 'account']):
            key = 'customer'
        elif any(s in subject_lower for s in ['supplier', 'vendor', 'provider']):
            key = 'supplier'
        elif any(s in subject_lower for s in ['sale', 'order', 'transaction', 'invoice']):
            key = 'sales'
        elif any(s in subject_lower for s in ['product', 'inventory', 'catalog', 'item']):
            key = 'product'
        elif any(s in subject_lower for s in ['support', 'ticket', 'help', 'issue']):
            key = 'support'
        schema = base_schemas[key].copy()
        if len(schema) < num_columns:
            schema = self._pad_schema(schema, num_columns, subject)
        return schema[:num_columns]
    def _pad_schema(self, schema: List[Dict], target: int, subject: str) :
        generic = [
            {"name": "CreatedDate", "type": "date", "examples": ["2024-01-15"], "description": "Record created"},
            {"name": "LastModified", "type": "date", "examples": ["2025-08-10"], "description": "Last updated"},
            {"name": "IsActive", "type": "boolean", "examples": ["True", "False"], "description": "Active status"},
            {"name": "Notes", "type": "text", "examples": ["", "Check details"], "description": "Additional notes"},
            {"name": "Status", "type": "category", "examples": ["Active", "Pending"], "description": "Status"},
            {"name": "Priority", "type": "category", "examples": ["Low", "Medium", "High"], "description": "Priority"},
            {"name": "Tags", "type": "text", "examples": ["tag1,tag2"], "description": "Tags"},
            {"name": "Source", "type": "category", "examples": ["Web", "Mobile", "API"], "description": "Data source"}
        ]
        while len(schema) < target and generic:
            schema.append(generic.pop(0))
        return schema[:target]
    def generate_lognormal_value(self, mean: float, stddev: float, 
                                 min_val: float, max_val: float) -> float:
        if mean <= 0:
            return random.uniform(min_val, max_val)
        mu = np.log(mean / np.sqrt(1 + (stddev/mean)**2))
        sigma = np.sqrt(np.log(1 + (stddev/mean)**2))
        value = np.random.lognormal(mu, sigma)
        return float(np.clip(value, min_val, max_val))
    def generate_normal_value(self, mean: float, stddev: float, 
                             min_val: float, max_val: float) -> float:
        value = np.random.normal(mean, stddev)
        return float(np.clip(value, min_val, max_val))
    def generate_power_law_value(self, alpha: float, min_val: int, max_val: int) :
        u = np.random.uniform(0, 1)
        value = min_val * (1 - u) ** (-1 / (alpha - 1))
        return int(np.clip(value, min_val, max_val))
    def generate_seasonal_multiplier(self, date: datetime, pattern: str = 'Q4_peak') :
        month = date.month
        quarter = (month - 1) // 3 + 1
        patterns = {
            'Q4_peak': {1: 0.85, 2: 0.9, 3: 0.95, 4: 1.0, 5: 1.0, 6: 1.05, 
                       7: 1.1, 8: 1.1, 9: 1.15, 10: 1.3, 11: 1.4, 12: 1.5},
            'Q2_Q3_peak': {1: 0.9, 2: 0.95, 3: 1.0, 4: 1.1, 5: 1.2, 6: 1.3,
                          7: 1.35, 8: 1.3, 9: 1.15, 10: 1.0, 11: 0.95, 12: 1.1},
            'uniform': {m: 1.0 for m in range(1, 13)}
        }
        return patterns.get(pattern, patterns['uniform']).get(month, 1.0)
    def generate_date(self,
                      start = None,
                      end = None,
                      date_format: str = "%Y-%m-%d",
                      prevent_future = None) -> str:
        def _coerce_date(value: Any) :
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"):
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
            return None
        options = getattr(self, "_active_generation_options", {}) or {}
        prevent_future = options.get('prevent_future', True) if prevent_future is None else prevent_future
        start = start or _coerce_date(options.get('date_min'))
        end = end or _coerce_date(options.get('date_max'))
        now = datetime.now()
        if prevent_future:
            if end is None or end > now:
                end = now
        elif end is None:
            future_days = int(options.get('future_days', 365))
            end = now + timedelta(days=future_days)
        if start is None:
            window_years = float(options.get('date_window_years', 5))
            window_days = max(30, int(window_years * 365))
            start = (end or now) - timedelta(days=window_days)
        if end is None:
            end = start + timedelta(days=365)
        if start > end:
            start, end = end, start
        delta_days = max((end - start).days, 0)
        random_days = random.randint(0, delta_days) if delta_days > 0 else 0
        generated = start + timedelta(days=random_days)
        return generated.strftime(date_format)
    def generate_person_name(self, country = None) :
        region_map = {
            'USA': 'Anglo', 'UK': 'Anglo', 'Canada': 'Anglo', 'Australia': 'Anglo',
            'Mexico': 'Hispanic', 'Spain': 'Hispanic',
            'China': 'East Asian', 'Japan': 'East Asian', 'Korea': 'East Asian',
            'India': 'South Asian',
            'Germany': 'European', 'France': 'European', 'Italy': 'European'
        }
        region = region_map.get(country, 'Anglo')
        name_set = self._INTERNATIONAL_NAMES.get(region, self._INTERNATIONAL_NAMES['Anglo'])
        return f"{random.choice(name_set['first'])} {random.choice(name_set['last'])}"
    def generate_company_name(self, subject = None) :
        industry = 'generic'
        if subject:
            sl = subject.lower()
            if any(s in sl for s in ['tech', 'software', 'it', 'digital']):
                industry = 'tech'
            elif any(s in sl for s in ['finance', 'banking', 'investment']):
                industry = 'finance'
            elif any(s in sl for s in ['manufact', 'industrial', 'supply']):
                industry = 'manufacturing'
            elif any(s in sl for s in ['health', 'medical', 'hospital']):
                industry = 'healthcare'
        keywords = self._INDUSTRY_KEYWORDS[industry]
        bases = ['Apex', 'Summit', 'Pinnacle', 'Starlight', 'Meridian', 'Global', 
                'Quantum', 'Premier', 'United', 'Pacific']
        style = random.random()
        if style < 0.4:
            return f"{random.choice(bases)} {random.choice(keywords)}"
        elif style < 0.7:
            last = random.choice(self._INTERNATIONAL_NAMES['Anglo']['last'])
            return f"{last} {random.choice(keywords)}"
        else:
            return f"{random.choice(bases)} {random.choice(self._INTERNATIONAL_NAMES['Anglo']['last'])} Inc."
    def generate_job_title(self, dept: str) :
        titles = {
            "IT": [
                "Software Engineer", "Senior Software Engineer", "Lead Software Engineer",
                "Network Engineer", "Systems Analyst", "DevOps Specialist", "IT Manager",
                "Database Administrator", "Security Analyst", "Cloud Architect"
            ],
            "Finance": [
                "Accountant", "Senior Accountant", "Financial Analyst", "Senior Financial Analyst",
                "Controller", "Compliance Officer", "Finance Manager", "Tax Specialist",
                "Budget Analyst", "Payroll Specialist"
            ],
            "HR": [
                "HR Coordinator", "Recruiter", "Senior Recruiter", "Benefits Specialist",
                "HR Manager", "Talent Acquisition Specialist", "HR Business Partner",
                "Training Coordinator", "Compensation Analyst"
            ],
            "Marketing": [
                "Marketing Coordinator", "Content Strategist", "Brand Manager", "Marketing Manager",
                "Digital Marketing Specialist", "SEO Specialist", "Social Media Manager",
                "Product Marketing Manager", "Marketing Analyst"
            ],
            "Operations": [
                "Operations Manager", "Operations Coordinator", "Logistics Coordinator",
                "Supply Chain Analyst", "Warehouse Manager", "Process Improvement Specialist",
                "Operations Analyst", "Facilities Manager"
            ],
            "Sales": [
                "Sales Representative", "Senior Sales Representative", "Account Manager",
                "Business Development Representative", "Sales Manager", "Account Executive",
                "Regional Sales Manager", "Sales Engineer", "Inside Sales Representative"
            ]
        }
        return random.choice(titles.get(dept, ["Specialist", "Coordinator", "Manager", "Analyst"]))
    def generate_phone(self, country: str = "USA") :
        country_normalized = country.upper() if country.upper() in ['USA', 'UK'] else country
        formats = {
            "US": lambda: f"+1 ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
            "CA": lambda: f"+1 ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
            "UK": lambda: f"+44 {random.randint(20,1999)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
            "DE": lambda: f"+49 {random.randint(30,9999)} {random.randint(1000000,99999999)}",
            "AU": lambda: f"+61 {random.randint(2,8)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
            "JP": lambda: f"+81 {random.randint(3,99)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
            "IN": lambda: f"+91 {random.randint(70000,99999)} {random.randint(10000,99999)}",
            "CN": lambda: f"+86 {random.randint(130,189)} {random.randint(1000,9999)} {random.randint(1000,9999)}",
            "FR": lambda: f"+33 {random.randint(1,9)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"
        }
        fmt = self._LOCATIONS.get(country_normalized, {}).get("phone_format", "US")
        return formats.get(fmt, formats["US"])()
    def generate_salary(self, job_title: str, country: str = "USA", 
                       department = None, years_experience: Optional[int] = None) -> float:
        base_ranges = {
            "USA": (35000, 150000), "UK": (28000, 120000),
            "Germany": (32000, 130000), "Canada": (33000, 125000),
            "Australia": (40000, 140000), "Japan": (30000, 110000),
            "India": (8000, 50000), "China": (12000, 60000), "France": (30000, 125000)
        }
        low, high = base_ranges.get(country, (30000, 120000))
        mult = self._LOCATIONS.get(country, {}).get('salary_multiplier', 1.0)
        low, high = int(low * mult), int(high * mult)
        h_mult = 1.0
        if any(t in job_title for t in ["CEO", "CFO", "CTO", "COO", "Chief"]):
            h_mult = random.uniform(2.3, 2.8)
        elif any(t in job_title for t in ["VP", "Vice President"]):
            h_mult = random.uniform(1.8, 2.2)
        elif any(t in job_title for t in ["Director", "Senior Director"]):
            h_mult = random.uniform(1.5, 1.8)
        elif any(t in job_title for t in ["Manager", "Lead"]):
            h_mult = random.uniform(1.2, 1.5)
        elif "Senior" in job_title:
            h_mult = random.uniform(1.15, 1.35)
        elif any(t in job_title for t in ["Junior", "Associate", "Assistant"]):
            h_mult = random.uniform(0.7, 0.9)
        elif any(t in job_title for t in ["Intern", "Trainee"]):
            h_mult = random.uniform(0.5, 0.7)
        d_mult = 1.0
        if department in ["IT", "Engineering"]:
            d_mult = random.uniform(1.12, 1.18)
        elif department in ["Finance", "Legal"]:
            d_mult = random.uniform(1.08, 1.14)
        elif department in ["Sales"]:
            d_mult = random.uniform(1.05, 1.12)
        elif department in ["Marketing"]:
            d_mult = random.uniform(1.02, 1.08)
        elif department in ["HR", "Operations"]:
            d_mult = random.uniform(0.98, 1.05)
        exp_mult = 1.0
        if years_experience is not None:
            if years_experience <= 10:
                exp_mult = 1.0 + (years_experience * random.uniform(0.02, 0.04))
            else:
                exp_mult = 1.0 + (10 * 0.03) + ((years_experience - 10) * random.uniform(0.01, 0.02))
        mean = (low + high * h_mult * d_mult * exp_mult) / 2
        stddev = (high - low) / 4
        salary = self.generate_lognormal_value(mean, stddev, low, high * h_mult * exp_mult)
        return round(salary / 100) * 100
    def generate_email(self, first_name: str, last_name: str, 
                      company = None) -> str:
        first = re.sub(r'[^a-zA-Z]', '', first_name.lower())
        last = re.sub(r'[^a-zA-Z]', '', last_name.lower())
        domain = company or random.choice(self._DOMAINS)
        if company and ' ' in company:
            domain = company.split()[0].lower() + '.com'
        formats = [
            f"{first}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first}.{last}{random.randint(1,99)}@{domain}"
        ]
        return random.choice(formats)
    def generate_id_with_encoding(self, prefix: str, row_idx: int, 
                                  encode_date: bool = False,
                                  location = None) -> str:
        prefix_offset = sum(ord(c) for c in prefix[:3]) * 1000
        seq = 100000 + prefix_offset + row_idx
        return f"{prefix}-{seq:06d}"
    def generate_id_with_encoding(self, prefix: str, index: int) :
        idx = int(index) if isinstance(index, (int, float)) else 0
        return f"{prefix}-{idx:05d}"
    def _strip_whitespace_from_text(self, df: pd.DataFrame) :
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].apply(lambda v: v.strip() if isinstance(v, str) else v)
        return df
    def _apply_category_standardization(self, df: pd.DataFrame, rules: List[Any]) :
        return df
    def _validate_all_dates_in_past(self, df: pd.DataFrame) :
        for c in df.columns:
            if 'date' in c.lower() or (df[c].dtype == object and all(isinstance(v, str) for v in df[c].dropna().head(5))):
                try:
                    formats_to_try = [
                        '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%Y',
                        '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S'
                    ]
                    parsed = None
                    for fmt in formats_to_try:
                        try:
                            candidate = pd.to_datetime(df[c], format=fmt, errors='coerce')
                        except Exception:
                            candidate = pd.to_datetime(df[c], errors='coerce')
                        if candidate.notna().any():
                            parsed = candidate
                            break
                    if parsed is None:
                        import warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            parsed = pd.to_datetime(df[c], errors='coerce')
                    if parsed is not None and parsed.notna().any():
                        df[c] = parsed.dt.strftime('%Y-%m-%d')
                except Exception:
                    pass
        return df
    def _apply_final_production_fixes(self, df: pd.DataFrame, subject: str) :
        cols = []
        seen = {}
        for col in df.columns:
            base = col
            if base in seen:
                seen[base] += 1
                col = f"{base}_{seen[base]}"
            else:
                seen[base] = 0
            cols.append(col)
        df.columns = cols
        return df
    def fix_employee_data_quality(self, df: pd.DataFrame, subject: str) :
        if 'Email' in df.columns:
            return df
        if 'FirstName' in df.columns and 'LastName' in df.columns:
            df['Email'] = df.apply(lambda r: self.generate_email(r['FirstName'], r['LastName']), axis=1)
    def _generate_customer_profiles_with_llm(self, count: int) :
        print(f" LLM Prompt: Generating {count} customer profiles...")
        try:
            prompt = f"""Generate {count} unique and realistic B2B customer company names.
            Include a mix of industries (Technology, Manufacturing, Healthcare, Finance, Retail).
            Return a JSON object with a key "companies" containing a list of objects, each with:
            - "name": The company name (creative, not just generic words)
            - "industry": The industry sector
            - "region_hint": A hint for location (e.g., "North America", "Europe", "Asia")
            Ensure names are diverse and sound like real businesses.
        Generate diverse product catalog using LLM, with deterministic fallback.
        Returns list of dicts with 'name', 'category', 'price'.
            response = self.generate_with_llm(prompt, cache_key=f"product_pool_{count}", max_tokens=4000)
            with open("llm_debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"\n--- PRODUCTS ({count}) ---\n{response}\n")
            data = self.extract_json(response)
            if data and 'products' in data and isinstance(data['products'], list):
                print(f"LLM generated {len(data['products'])} products")
                return data['products'][:count]
        except Exception as e:
            print(f" LLM Product generation failed: {e}")
        print(" Using deterministic fallback for products")
        fallback_products = []
        categories = ['Electronics', 'Apparel', 'Home Goods', 'Outdoor Gear', 'Automotive']
        for _ in range(count):
            category = random.choice(categories)
            if category == 'Electronics':
                items = [('Quantum', 'Display', 799.99, 3499.99), ('Acoustic', 'Headphones', 99.99, 399.99), ('Volt', 'Charger', 29.99, 79.99)]
            elif category == 'Apparel':
                items = [('Trek', 'Jacket', 89.99, 299.99), ('Urban', 'Jeans', 59.99, 129.99), ('Active', 'T-Shirt', 19.99, 49.99)]
            elif category == 'Home Goods':
                items = [('Aero', 'Coffee Maker', 24.99, 199.99), ('Cozy', 'Blanket', 39.99, 149.99), ('Chef', 'Knife Set', 79.99, 499.99)]
            elif category == 'Outdoor Gear':
                items = [('Summit', 'Backpack', 149.99, 349.99), ('Trail', 'Tent', 199.99, 499.99), ('Blaze', 'Headlamp', 49.99, 99.99)]
            else:
                items = [('Synthetic', 'Motor Oil', 35.00, 65.00), ('Hydro', 'Wiper Blade', 15.00, 30.00), ('Premium', 'Air Filter', 19.99, 59.99)]
            item = random.choice(items)
            name = f"{item[0]} {item[1]}"
            price = round(random.uniform(item[2], item[3]), 2)
            fallback_products.append({'name': name, 'category': category, 'price': price})
        return fallback_products
    def generate_sales_transactions_with_entities(self, rows: int, columns: int, subject: str) :
        print("=" * 80)
        print("GENERATING FINANCIAL TRANSACTIONS WITH ENTITY-BASED APPROACH")
        print("=" * 80)
        date_min = datetime(2020, 1, 1)
        date_max = datetime(2025, 11, 12)
        days_range = (date_max - date_min).days
        num_customers = random.randint(30, 40)
        print(f"Creating {num_customers} customers...")
        customers = []
        customer_profiles = self._generate_customer_profiles_with_llm(num_customers)
        if len(customer_profiles) < num_customers:
             while len(customer_profiles) < num_customers:
                 customer_profiles.append(random.choice(customer_profiles))
        for i in range(num_customers):
            profile = customer_profiles[i]
            company_name = profile.get('name', f"Customer {i}")
            country = random.choice(list(self._LOCATIONS.keys()))
            city = random.choice(self._LOCATIONS[country]['cities'])
            max_creation_date = date_max - timedelta(days=90)
            creation_days_available = (max_creation_date - date_min).days
            created_days_offset = random.randint(0, creation_days_available)
            created_date = date_min + timedelta(days=created_days_offset)
            customers.append({
                'CustomerID': f"CUST-{1000+i}",
                'CustomerName': company_name,
                'Country': country,
                'City': city,
                'Region': random.choice(self._LOCATIONS[country]['states']),
                'CreatedDate': created_date
            })
        num_reps = random.randint(8, 12)
        print(f"Creating {num_reps} sales representatives...")
        sales_reps = [self.generate_person_name() for _ in range(num_reps)]
        for customer in customers:
            customer['PrimarySalesRep'] = random.choice(sales_reps)
        num_products = random.randint(50, 80)
        print(f"Creating {num_products} products...")
        product_pool = self._generate_product_pool_with_llm(num_products)
        if len(product_pool) < num_products:
             while len(product_pool) < num_products:
                 product_pool.append(random.choice(product_pool))
        products = []
        for i in range(num_products):
            item = product_pool[i]
            products.append({
                'ProductSKU': f"PRO-{341000 + i}",
                'ProductName': item.get('name', f"Product {i}"),
                'Category': item.get('category', 'General'),
                'UnitPrice': float(item.get('price', 99.99))
            })
        if rows >= 50:
            pass
        num_products = len(products)
        popularity_weights = np.zeros(num_products)
        popularity_weights[0] = 0.10
        if num_products >= 5:
            tier2_per_product = 0.25 / 4
            for i in range(1, 5):
                popularity_weights[i] = tier2_per_product
        remaining_products = num_products - 5
        if remaining_products > 0:
            tier3_per_product = 0.55 / remaining_products
            for i in range(5, num_products):
                popularity_weights[i] = tier3_per_product
        else:
            total_assigned = 0.35 if num_products >= 5 else (0.10 + (num_products - 1) * 0.25 / 4)
            remaining = 1.0 - total_assigned
            for i in range(num_products):
                popularity_weights[i] += remaining / num_products
        popularity_weights = popularity_weights / popularity_weights.sum()
        print(f"Created {len(products)} products with constrained popularity distribution")
        print(f"Top product: {popularity_weights[0]:.1%}")
        if num_products >= 5:
            print(f"Next 4 products: {popularity_weights[1]:.1%} each")
        if num_products > 5:
            print(f"Remaining {num_products-5} products: {popularity_weights[5]:.1%} each")
        print(f"Top 5 total: {np.sum(popularity_weights[:min(5, num_products)]):.1%}")
        print(f"Generating {rows} orders...")
        customer_weights = np.random.pareto(1.5, num_customers) + 1
        customer_weights = customer_weights / customer_weights.sum()
        max_weight_idx = np.argmax(customer_weights)
        if customer_weights[max_weight_idx] > 0.12:
            excess = customer_weights[max_weight_idx] - 0.12
            customer_weights[max_weight_idx] = 0.12
            other_indices = [i for i in range(num_customers) if i != max_weight_idx]
            for idx in other_indices:
                customer_weights[idx] += excess / len(other_indices)
        orders = []
        order_ids = set()
        while len(order_ids) < rows:
            order_ids.add(f"ORD-{random.randint(400000, 500000)}")
        order_id_list = list(order_ids)
        for i in range(rows):
            customer_idx = np.random.choice(range(num_customers), p=customer_weights)
            customer = customers[customer_idx]
            product_idx = np.random.choice(len(products), p=popularity_weights)
            product = products[product_idx]
            created_date = customer['CreatedDate']
            days_after_created = random.randint(1, 90)
            order_date = created_date + timedelta(days=days_after_created)
            if order_date > date_max:
                order_date = date_max - timedelta(days=random.randint(1, 30))
            unit_price = product['UnitPrice']
            if unit_price > 1000:
                if random.random() < 0.05:
                    quantity = random.randint(3, 5)
                else:
                    quantity = random.randint(1, 2)
            elif unit_price > 500:
                if random.random() < 0.05:
                    quantity = random.randint(4, 5)
                else:
                    quantity = random.randint(1, 3)
            elif unit_price >= 200:
                quantity = random.randint(1, 5)
            elif unit_price >= 100:
                quantity = random.randint(1, 10)
            else:
                quantity = random.randint(1, 20)
            total_sale = round(quantity * product['UnitPrice'], 2)
            order_id = order_id_list[i]
            days_ago = (date_max - order_date).days
            if days_ago < 14:
                status = random.choices(
                    ['Pending', 'Completed', 'Pending'],
                    weights=[0.6, 0.3, 0.1],
                    k=1
                )[0]
            elif days_ago < 60:
                status = random.choices(
                    ['Completed', 'Pending', 'Cancelled'],
                    weights=[0.75, 0.10, 0.15],
                    k=1
                )[0]
            else:
                status = random.choices(
                    ['Completed', 'Cancelled', 'Refunded'],
                    weights=[0.75, 0.10, 0.15],
                    k=1
                )[0]
            if random.random() < 0.85:
                sales_rep = customer['PrimarySalesRep']
            else:
                sales_rep = random.choice([r for r in sales_reps if r != customer['PrimarySalesRep']])
            order = {
                'OrderID': order_id,
                'OrderDate': order_date.strftime('%Y-%m-%d'),
                'CustomerID': customer['CustomerID'],
                'CustomerName': customer['CustomerName'],
                'ProductSKU': product['ProductSKU'],
                'ProductName': product['ProductName'],
                'Category': product['Category'],
                'Quantity': quantity,
                'UnitPrice': product['UnitPrice'],
                'TotalSale': total_sale,
                'SalesRep': sales_rep,
                'Region': customer['Region'],
                'Status': status,
                'CreatedDate': created_date.strftime('%Y-%m-%d')
            }
            orders.append(order)
        df = pd.DataFrame(orders)
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS:")
        print("=" * 80)
        try:
            assert df['OrderID'].notna().all(), "OrderID has null values!"
            assert df['OrderID'].is_unique, "OrderID has duplicates!"
            print(f"OrderID: {len(df)} unique values")
            df['OrderDate_dt'] = pd.to_datetime(df['OrderDate'])
            df['CreatedDate_dt'] = pd.to_datetime(df['CreatedDate'])
            assert df['OrderDate_dt'].min() >= datetime(2020, 1, 1), "OrderDate has dates before 2020-01-01!"
            assert df['OrderDate_dt'].max() <= datetime(2025, 11, 12), "OrderDate max violated!"
            assert df['CreatedDate_dt'].min() >= datetime(2020, 1, 1), "CreatedDate has dates before 2020-01-01!"
            assert df['CreatedDate_dt'].max() <= datetime(2025, 11, 12), "CreatedDate max violated!"
            print(f"Date ranges: Orders {df['OrderDate_dt'].min().strftime('%Y-%m-%d')} to {df['OrderDate_dt'].max().strftime('%Y-%m-%d')}")
            print(f"  Created {df['CreatedDate_dt'].min().strftime('%Y-%m-%d')} to {df['CreatedDate_dt'].max().strftime('%Y-%m-%d')}")
            assert (df['CreatedDate_dt'] <= df['OrderDate_dt']).all(), "CreatedDate after OrderDate (temporal violation)!"
            time_gaps = (df['OrderDate_dt'] - df['CreatedDate_dt']).dt.days
            print(f" Temporal logic: CreatedDate <= OrderDate (gap: 1-90 days mean={time_gaps.mean():.1f})")
            assert df['SalesRep'].notna().all(), f"SalesRep has {df['SalesRep'].isna().sum()} null values!"
            print(f" SalesRep: All {len(df)} records have sales representative assigned")
            customer_dist = df['CustomerID'].value_counts()
            top_customer_pct = customer_dist.iloc[0] / len(df)
            top_5_pct = customer_dist.head(5).sum() / len(df)
            print(f" Customer distribution:")
            print(f"Top customer: {top_customer_pct:.1%} ({customer_dist.iloc[0]} orders)")
            print(f"Top 5 customers: {top_5_pct:.1%} ({customer_dist.head(5).sum()} orders)")
            print(f"Unique customers: {df['CustomerID'].nunique()}")
            valid_statuses = {'Completed', 'Pending', 'Cancelled', 'Refunded'}
            invalid_statuses = set(df['Status'].unique()) - valid_statuses
            assert len(invalid_statuses) == 0, f"Invalid statuses found: {invalid_statuses}"
            status_dist = df['Status'].value_counts()
            print(f" Status distribution (valid only):")
            for status, count in status_dist.items():
                print(f"   {status}: {count/len(df):.1%} ({count} orders)")
            expensive = df[df['UnitPrice'] > 500]
            if len(expensive) > 0:
                assert expensive['Quantity'].max() <= 5, "Quantity constraint violated!"
                premium = df[df['UnitPrice'] > 1000]
                if len(premium) > 0:
                    assert premium['Quantity'].max() <= 5, "Quantity constraint violated!"
                print(f" Quantity constraints:")
                print(f"   Premium (>$1000): {len(premium)} items, max quantity={premium['Quantity'].max()}")
                print(f"   Expensive ($500-$1000): {len(expensive) - len(premium)} items, max quantity={expensive['Quantity'].max()}")
            highvalue = df[(df['UnitPrice'] >= 200) & (df['UnitPrice'] <= 500)]
            if len(highvalue) > 0:
                print(f"   High-value ($200-$500): {len(highvalue)} items, max quantity={highvalue['Quantity'].max()}")
            medium = df[(df['UnitPrice'] >= 100) & (df['UnitPrice'] < 200)]
            if len(medium) > 0:
                print(f"   Medium ($100-$200): {len(medium)} items, max quantity={medium['Quantity'].max()}")
            cheap = df[df['UnitPrice'] < 100]
            if len(cheap) > 0:
                print(f"   Low-cost (<$100): {len(cheap)} items, max quantity={cheap['Quantity'].max()}")
            product_dist = df['ProductSKU'].value_counts()
            top_product_pct = product_dist.iloc[0] / len(df)
            top_5_products_pct = product_dist.head(5).sum() / len(df)
            assert top_product_pct <= 0.15, "Top product distribution violated!"
            assert top_5_products_pct <= 0.45, "Top 5 product distribution violated!"
            print(f" Product distribution (constrained Pareto with sampling tolerance):")
            print(f"   Top product: {top_product_pct:.1%} ({product_dist.iloc[0]} orders) [target: 8-12%]")
            print(f"   Top 5 products: {top_5_products_pct:.1%} ({product_dist.head(5).sum()} orders) [target: 30-40%]")
            remaining_pct = (len(df) - product_dist.head(5).sum()) / len(df)
            print(f"   Remaining {len(product_dist)-5} products: {remaining_pct:.1%} ({len(df)-product_dist.head(5).sum()} orders)")
            print(f"   Unique products: {df['ProductSKU'].nunique()}")
            customer_rep_map = df.groupby('CustomerID')['SalesRep'].nunique()
            primary_rep_consistency = (customer_rep_map == 1).sum() / len(customer_rep_map)
            print(f" Customer-SalesRep consistency: {primary_rep_consistency:.1%} customers use single primary rep")
            calc_total = (df['Quantity'] * df['UnitPrice']).round(2)
            assert (df['TotalSale'] == calc_total).all(), "TotalSale calculation error!"
            print(f" TotalSale calculation: All {len(df)} records correct")
            repeat_rate = 1 - (df['CustomerID'].nunique() / len(df))
            print(f" Repeat customer rate: {repeat_rate:.1%}")
            print(f" Sales reps: {df['SalesRep'].nunique()} unique representatives")
            print("=" * 80)
            print(" ALL VALIDATIONS PASSED - DATA IS READY\n")
            df = df.drop(['OrderDate_dt', 'CreatedDate_dt'], axis=1)
        except AssertionError as e:
            print(f" VALIDATION FAILED: {e}")
            raise
        return df
    def generate_excel_data(self, rows: int, columns: int, subject: str, 
                           options = None) -> pd.DataFrame:
        print(f" Starting generation for '{subject}' — {rows}×{columns}")
        schema = self.generate_column_headers_with_llm(subject, columns)
        subject_lower = subject.lower()
        previous_options = getattr(self, "_active_generation_options", {})
        self._active_generation_options = (options or {}).copy()
        is_financial_trans = 'financial' in subject_lower and 'transaction' in subject_lower
        is_sales = any(kw in subject_lower for kw in ['sales', 'transaction', 'order', 'invoice']) and not is_financial_trans
        is_product = any(kw in subject_lower for kw in ['product', 'catalog', 'catalogue', 'inventory', 'item'])
        result_df: pd.DataFrame
        try:
            if is_product:
                print("Using LLM-driven product catalogue generator")
                result_df = self.generate_product_catalog_with_llm(rows, columns, subject, schema)
            else:
                is_employee = any(kw in subject_lower for kw in ['employee', 'staff', 'workforce', 'personnel', 'hr'])
                if is_employee:
                    print("Using specialized employee data generator")
                    result_df = self.generate_employee_data(rows, columns, subject)
                else:
                    print("Using generic LLM-driven generator")
                    result_df = self._generate_generic_data(rows, columns, subject, schema)
        finally:
            self._active_generation_options = previous_options
        return result_df
    def generate_product_catalog_with_llm(self, rows: int, columns: int, 
                                          subject: str, schema: List[Dict]) -> pd.DataFrame:
        print(f" Generating {rows} products via LLM with STRICT realism constraints")
        PRODUCT_CATALOG = {
            'Electronics': {
                'HDMI Cable 6-ft': (5.99, 14.99),
                'HDMI Cable 10-ft': (7.99, 19.99),
                'DP to HDMI Adapter': (9.99, 24.99),
                'USB-C Hub 7-in-1': (19.99, 49.99),
                'Wireless Mouse': (12.99, 49.99),
                'Gaming Mouse': (24.99, 79.99),
                'Mechanical Keyboard RGB': (49.99, 149.99),
                'USB-C Charging Cable': (8.99, 19.99),
                'USB-C Charging Cable 3-pack': (15.99, 39.99),
                'Phone Screen Protector': (4.99, 14.99),
                'Webcam 1080p': (29.99, 89.99),
                'Wireless Earbuds Pro': (49.99, 149.99),
                'Wireless Noise-Canceling Headphones': (79.99, 299.99),
                'Bluetooth Speaker': (24.99, 149.99),
                'Digital Camera 24MP': (249.99, 799.99),
                'Digital Camera 48MP Pro': (599.99, 1499.99),
                'Laptop 13-inch i5': (499.99, 899.99),
                'Laptop 15-inch i7': (799.99, 1699.99),
                'Laptop 15-inch i9': (1299.99, 2499.99),
                'Tablet 10-inch': (149.99, 399.99),
                'Tablet Pro 12-inch': (399.99, 899.99),
                '4K Smart TV 55-inch': (349.99, 699.99),
                '4K Smart TV 65-inch': (499.99, 1099.99),
                '4K Smart TV 75-inch': (799.99, 1999.99),
                'Portable SSD 1TB': (79.99, 149.99),
                'Portable SSD 2TB': (149.99, 299.99),
                'External Hard Drive 2TB': (49.99, 99.99),
                'USB 3.0 Flash Drive 64GB': (9.99, 24.99),
                'USB 3.0 Flash Drive 128GB': (14.99, 39.99),
                'Monitor 27-inch': (149.99, 399.99),
                'Monitor 32-inch': (249.99, 599.99),
            },
            'Automotive': {
                'Synthetic Motor Oil 5W-30': (19.99, 39.99),
                'Synthetic Motor Oil 10W-40': (21.99, 42.99),
                'Conventional Motor Oil 10W-30': (12.99, 24.99),
                'Brake Pad Set Front': (34.99, 79.99),
                'Brake Pad Set Rear': (29.99, 69.99),
                'Spark Plugs Set of 4': (12.99, 39.99),
                'Air Filter Standard': (12.99, 29.99),
                'Air Filter High-Flow': (19.99, 39.99),
                'Cabin Air Filter': (14.99, 34.99),
                'LED Headlight Bulbs H7': (24.99, 54.99),
                'LED Headlight Bulbs H11': (24.99, 54.99),
                'Windshield Wiper Blades 24-inch': (14.99, 29.99),
                'Windshield Wiper Blades 28-inch': (14.99, 34.99),
                'Battery 12V 100Ah': (79.99, 199.99),
                'Battery 12V 50Ah': (49.99, 129.99),
                'Floor Mats Set': (24.99, 59.99),
                'Car Air Freshener': (2.99, 9.99),
                'Oil Filter': (8.99, 19.99),
                'Coolant Antifreeze': (12.99, 29.99),
                'Transmission Fluid': (14.99, 34.99),
                'Tire Sealant': (9.99, 24.99),
                'Tire Pressure Gauge': (7.99, 19.99),
                'Jump Starter Battery Pack': (39.99, 129.99),
            },
            'Apparel': {
                "Men's Cotton T-Shirt White": (9.99, 24.99),
                "Men's Cotton T-Shirt Black": (9.99, 24.99),
                "Men's Cotton T-Shirt Navy": (9.99, 24.99),
                "Men's Button-Up Shirt": (24.99, 59.99),
                "Men's Polo Shirt": (19.99, 49.99),
                "Women's Cotton T-Shirt": (9.99, 24.99),
                "Women's Running Shoes": (59.99, 159.99),
                "Women's Running Shoes Pro": (79.99, 179.99),
                "Women's Yoga Shoes": (49.99, 119.99),
                "Men's Running Shoes": (59.99, 159.99),
                'Denim Jeans Blue': (34.99, 79.99),
                'Denim Jeans Black': (34.99, 79.99),
                'Denim Jeans Skinny': (34.99, 89.99),
                'Hoodie Sweatshirt Grey': (29.99, 69.99),
                'Hoodie Sweatshirt Black': (29.99, 69.99),
                'Athletic Shorts': (19.99, 49.99),
                'Yoga Pants': (34.99, 79.99),
                'Socks Crew 6-pack': (9.99, 19.99),
                'Winter Beanie': (9.99, 24.99),
                'Baseball Cap': (12.99, 29.99),
                'Leather Belt': (19.99, 54.99),
                'Formal Dress Pants': (49.99, 129.99),
                "Women's Cardigan": (34.99, 89.99),
                "Women's Blazer": (59.99, 159.99),
                'Casual Sneakers': (39.99, 99.99),
                'Hiking Boots': (79.99, 199.99),
                'Winter Jacket Waterproof': (89.99, 249.99),
                'Winter Jacket Insulated': (79.99, 199.99),
            },
            'Home Goods': {
                'Stainless Steel Cookware Set 10-piece': (79.99, 199.99),
                'Stainless Steel Cookware Set 15-piece': (99.99, 249.99),
                'Memory Foam Pillow': (24.99, 74.99),
                'Down Alternative Pillow': (34.99, 89.99),
                'LED Desk Lamp Warm': (19.99, 54.99),
                'LED Desk Lamp Cool White': (19.99, 54.99),
                'Floor Lamp Arc': (39.99, 129.99),
                'Coffee Maker 12-cup': (39.99, 89.99),
                'Coffee Maker Single Serve': (49.99, 129.99),
                'Espresso Machine': (149.99, 399.99),
                'Vacuum Cleaner Upright': (149.99, 399.99),
                'Vacuum Cleaner Robot': (249.99, 699.99),
                'Microwave Oven 1000W': (59.99, 149.99),
                'Toaster 4-slice': (34.99, 79.99),
                'Blender 1000W': (49.99, 129.99),
                'Food Processor': (59.99, 159.99),
                'Cutting Board Set': (14.99, 39.99),
                'Knife Block Set': (34.99, 99.99),
                'Sheet Set Queen': (29.99, 79.99),
                'Sheet Set King': (39.99, 99.99),
                'Duvet Cover King': (34.99, 89.99),
                'Throw Blanket': (24.99, 59.99),
                'Area Rug 5x7': (79.99, 249.99),
                'Dining Table Set': (299.99, 799.99),
                'Office Chair': (129.99, 349.99),
            },
            'Outdoor Gear': {
                'Camping Tent 2-Person': (49.99, 149.99),
                'Camping Tent 4-Person': (79.99, 199.99),
                'Camping Tent 6-Person': (119.99, 299.99),
                'Camping Tent Dome': (59.99, 169.99),
                'Hiking Backpack 50L': (79.99, 199.99),
                'Hiking Backpack 70L': (99.99, 249.99),
                'Hiking Backpack 40L': (59.99, 149.99),
                'Sleeping Bag Summer': (34.99, 89.99),
                'Sleeping Bag Winter': (59.99, 169.99),
                'Sleeping Bag 3-Season': (44.99, 119.99),
                'Portable Camping Stove': (24.99, 69.99),
                'Camping Cooler 45L': (39.99, 99.99),
                'Camping Cooler 70L': (59.99, 149.99),
                'Water Bottle 1L': (12.99, 29.99),
                'Water Bottle 2L Insulated': (29.99, 59.99),
                'Water Bottle 3L Hydration': (34.99, 79.99),
                'Camping Pillow': (14.99, 39.99),
                'Tent Footprint': (19.99, 49.99),
                'Camping Headlamp': (19.99, 59.99),
                'Multi-tool': (24.99, 89.99),
                'Compass': (9.99, 24.99),
                'Rope 50-ft': (12.99, 34.99),
                'Flashlight LED': (14.99, 49.99),
                'Hiking Boots Waterproof': (79.99, 199.99),
                'Climbing Harness': (34.99, 99.99),
                'Carabiners Set': (14.99, 39.99),
            }
        }
        print(" Requesting product names from LLM...")
        product_names = self._generate_product_names_from_llm(rows, subject)
        if not product_names or len(product_names) < rows:
            print(f"   LLM returned {len(product_names) if product_names else 0} names, using deterministic fallback")
            product_names = self._generate_fallback_product_names(rows)
        print(" Assigning categories based on product type...")
        categories_list = []
        assigned_products = []
        for product_name in product_names:
            assigned = False
            for category, products_dict in PRODUCT_CATALOG.items():
                if product_name in products_dict:
                    categories_list.append(category)
                    assigned_products.append(product_name)
                    assigned = True
                    break
            if not assigned:
                if any(kw in product_name.lower() for kw in ['shirt', 't-shirt', 'jeans', 'shoes', 'hoodie', 'shorts', 'pants', 'jacket', 'socks', 'hat', 'beanie', 'cap', 'blazer', 'cardigan', 'boots', 'sneakers']):
                    categories_list.append('Apparel')
                    assigned_products.append(product_name)
                elif any(kw in product_name.lower() for kw in ['motor oil', 'brake', 'spark plug', 'filter', 'battery', 'wiper', 'transmission', 'coolant', 'tire']):
                    categories_list.append('Automotive')
                    assigned_products.append(product_name)
                elif any(kw in product_name.lower() for kw in ['tent', 'backpack', 'sleeping bag', 'camping', 'hiking', 'outdoor', 'water bottle', 'stove', 'cooler', 'headlamp']):
                    categories_list.append('Outdoor Gear')
                    assigned_products.append(product_name)
                elif any(kw in product_name.lower() for kw in ['lamp', 'cookware', 'pillow', 'coffee', 'vacuum', 'microwave', 'toaster', 'blender', 'knife', 'sheet', 'blanket', 'rug', 'furniture', 'chair']):
                    categories_list.append('Home Goods')
                    assigned_products.append(product_name)
                else:
                    categories_list.append('Electronics')
                    assigned_products.append(product_name)
        print(f"Assigned {len(set(categories_list))} unique categories")
        print(" Generating realistic prices by product type...")
        prices_list = []
        for product_name, category in zip(assigned_products, categories_list):
            price_range = (5.99, 199.99)
            if category in PRODUCT_CATALOG and product_name in PRODUCT_CATALOG[category]:
                price_range = PRODUCT_CATALOG[category][product_name]
            price = round(random.uniform(price_range[0], price_range[1]), 2)
            prices_list.append(price)
        print(f"   Price range: ${min(prices_list):.2f} - ${max(prices_list):.2f}")
        print(f" Building {rows} products with structured business logic...")
        dataset = {}
        now = datetime.now()
        date_min = datetime(2020, 1, 1)
        date_max = datetime(2025, 11, 12)
        days_range = (date_max - date_min).days
        for col_schema in schema:
            col_name = col_schema.get('name', 'Field')
            col_type = col_schema.get('type', 'text')
            col_data = []
            if 'product' in col_name.lower() and 'id' in col_name.lower() and col_type == 'id':
                col_data = [f"PRO-{i:06d}" for i in range(rows)]
            elif 'name' in col_name.lower() and 'product' in col_name.lower():
                col_data = assigned_products[:rows]
            elif col_name.lower() in ('sku', 'productsku'):
                col_data = [f"SKU-{i:06d}" for i in range(rows)]
            elif 'category' in col_name.lower():
                col_data = categories_list[:rows]
                dataset['_categories'] = col_data
            elif 'price' in col_name.lower() and 'list' not in col_name.lower():
                col_data = prices_list[:rows]
                dataset['_prices'] = col_data
            elif 'cost' in col_name.lower():
                prices = dataset.get('_prices', prices_list)
                cost_ratio = [random.uniform(0.70, 0.85) for _ in range(rows)]
                col_data = [round(p * r, 2) for p, r in zip(prices, cost_ratio)]
            elif any(k in col_name.lower() for k in ['stock', 'stockquantity']):
                prices = dataset.get('_prices', prices_list)
                col_data = []
                for price in prices:
                    if price < 50:
                        stock = random.randint(50, 300)
                    elif price < 200:
                        stock = random.randint(20, 150)
                    elif price < 500:
                        stock = random.randint(5, 50)
                    else:
                        stock = random.randint(1, 20)
                    col_data.append(stock)
            elif 'reorder' in col_name.lower():
                prices = dataset.get('_prices', prices_list)
                stock_col = dataset.get('StockQuantity', [random.randint(10, 100) for _ in range(rows)])
                col_data = []
                for stock in stock_col:
                    reorder = max(5, int(stock * random.uniform(0.15, 0.30)))
                    col_data.append(min(50, reorder))
            elif 'supplier' in col_name.lower():
                suppliers = [self.generate_company_name(subject) for _ in range(min(12, rows // 5))]
                col_data = random.choices(suppliers, k=rows)
            elif 'dateadded' in col_name.lower():
                col_data = []
                for _ in range(rows):
                    random_days = random.randint(0, days_range)
                    date_val = (date_min + timedelta(days=random_days))
                    if date_val > date_max:
                        date_val = date_max
                    col_data.append(date_val.strftime('%Y-%m-%d'))
                dataset['_dates_added'] = col_data
            elif 'createddate' in col_name.lower():
                dates_added = dataset.get('_dates_added', None)
                col_data = []
                for da_str in (dates_added if dates_added else [(date_min + timedelta(days=random.randint(0, days_range))).strftime('%Y-%m-%d')] * rows):
                    da = datetime.strptime(da_str, '%Y-%m-%d')
                    days_after = random.randint(0, 30)
                    cd = da + timedelta(days=days_after)
                    if cd > date_max:
                        cd = date_max
                    col_data.append(cd.strftime('%Y-%m-%d'))
                dataset['_dates_created'] = col_data
            elif 'lastmodified' in col_name.lower() or 'modified' in col_name.lower():
                dates_created = dataset.get('_dates_created', None)
                col_data = []
                for dc_str in (dates_created if dates_created else [(date_min + timedelta(days=random.randint(0, days_range))).strftime('%Y-%m-%d')] * rows):
                    dc = datetime.strptime(dc_str, '%Y-%m-%d')
                    days_after = random.randint(0, 365)
                    lm = dc + timedelta(days=days_after)
                    if lm > date_max:
                        lm = date_max
                    col_data.append(lm.strftime('%Y-%m-%d'))
            elif 'isactive' in col_name.lower():
                col_data = random.choices([True, False], weights=[0.85, 0.15], k=rows)
            elif 'notes' in col_name.lower():
                notes = ['', 'Check stock levels', 'High demand', 'New supplier', 'Seasonal', 'Discontinued']
                col_data = random.choices(notes, k=rows)
            elif 'status' in col_name.lower():
                statuses = ['Active', 'Inactive', 'Pending', 'Discontinued']
                col_data = random.choices(statuses, k=rows)
            else:
                if col_type == 'id':
                    prefix = re.sub(r'[^A-Z]', '', col_name[:3].upper() or "FLD")
                    col_data = [f"{prefix}-{i:05d}" for i in range(rows)]
                elif col_type == 'money':
                    col_data = [round(random.uniform(10.0, 200.0), 2) for _ in range(rows)]
                elif col_type == 'number':
                    col_data = [random.randint(0, 500) for _ in range(rows)]
                elif col_type == 'date':
                    col_data = [(date_min + timedelta(days=random.randint(0, days_range))).strftime('%Y-%m-%d') for _ in range(rows)]
                else:
                    col_data = [f"{col_name}_{i+1}" for i in range(rows)]
            if col_data and len(col_data) == rows:
                dataset[col_name] = col_data
            elif col_data:
                dataset[col_name] = (col_data * ((rows // len(col_data)) + 1))[:rows]
            else:
                dataset[col_name] = [f"{col_name}_{i+1}" for i in range(rows)]
        df = pd.DataFrame(dataset)
        for marker in ['_categories', '_prices', '_dates_added', '_dates_created']:
            if marker in df.columns:
                df = df.drop(marker, axis=1)
        df = self._strip_whitespace_from_text(df)
        df = self._apply_final_production_fixes(df, subject)
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS:")
        print("=" * 80)
        try:
            if 'ProductName' in df.columns:
                unique_names = df['ProductName'].nunique()
                print(f" ProductName: {unique_names} unique out of {len(df)}")
                min_unique = max(1, int(len(df) * 0.20))
                assert unique_names >= min_unique, f"Not enough unique names: {unique_names} (need at least {min_unique})"
            if 'Category' in df.columns:
                categories = df['Category'].value_counts()
                print(f" Categories: {len(categories)} types - {dict(categories)}")
            if 'Price' in df.columns and 'Cost' in df.columns:
                df['Price_check'] = pd.to_numeric(df['Price'], errors='coerce')
                df['Cost_check'] = pd.to_numeric(df['Cost'], errors='coerce')
                valid_prices = df['Price_check'].notna().sum()
                print(f" Price: {valid_prices}/{len(df)} valid numeric values (${df['Price_check'].min():.2f} - ${df['Price_check'].max():.2f})")
                assert valid_prices >= len(df) * 0.95, "Too many non-numeric prices"
                cost_ratio = (df['Cost_check'] / df['Price_check']).dropna()
                print(f" Cost/Price: {cost_ratio.mean():.1%} mean ratio (70-85% constraint)")
                df = df.drop(['Price_check', 'Cost_check'], axis=1)
            if 'DateAdded' in df.columns:
                dates = pd.to_datetime(df['DateAdded'], errors='coerce')
                valid_dates = dates.notna().sum()
                min_date = dates.min()
                max_date = dates.max()
                print(f" DateAdded: {valid_dates}/{len(df)} valid dates ({min_date.date()} to {max_date.date()})")
                assert max_date <= datetime(2025, 11, 12), "Date exceeds max!"
            print("=" * 80)
            print(f" ALL VALIDATIONS PASSED")
        except AssertionError as e:
            print(f" VALIDATION FAILED: {e}")
            raise
        print(f" Product catalogue generation complete: {len(df)} rows × {len(df.columns)} columns")
        df = self._apply_product_catalog_business_rules(df)
        return df
    def _apply_product_catalog_business_rules(self, df: pd.DataFrame) :
        print("🔧 Applying product catalogue business rules...")
        fixes_applied = []
        if 'IsActive' in df.columns and 'Status' in df.columns:
            conflicts_before = (
                ((df['IsActive'] == True) & (df['Status'].isin(['Inactive', 'Discontinued']))).sum() +
                ((df['IsActive'] == False) & (df['Status'] == 'Active')).sum()
            )
            df.loc[df['Status'] == 'Active', 'IsActive'] = True
            df.loc[df['Status'].isin(['Inactive', 'Discontinued']), 'IsActive'] = False
            if conflicts_before > 0:
                fixes_applied.append(f"Synchronized IsActive/Status for {conflicts_before} records")
        if 'Status' in df.columns:
            discontinued_mask = df['Status'] == 'Discontinued'
            products_fixed = 0
            if 'StockQuantity' in df.columns:
                products_with_stock = (discontinued_mask & (df['StockQuantity'] > 0)).sum()
                if products_with_stock > 0:
                    df.loc[discontinued_mask, 'StockQuantity'] = 0
                    products_fixed += products_with_stock
            if 'ReorderLevel' in df.columns:
                df.loc[discontinued_mask, 'ReorderLevel'] = 0
            if products_fixed > 0:
                fixes_applied.append(f"Cleared inventory for {products_fixed} discontinued products")
        date_cols_to_check = []
        if 'DateAdded' in df.columns:
            date_cols_to_check.append('DateAdded')
        if 'CreatedDate' in df.columns:
            date_cols_to_check.append('CreatedDate')
        if 'LastModified' in df.columns:
            date_cols_to_check.append('LastModified')
        if len(date_cols_to_check) >= 2:
            for col in date_cols_to_check:
                df[f'{col}_dt'] = pd.to_datetime(df[col], errors='coerce')
            date_fixes = 0
            if 'DateAdded_dt' in df.columns and 'CreatedDate_dt' in df.columns:
                bad_created = (df['CreatedDate_dt'] < df['DateAdded_dt'])
                if bad_created.any():
                    df.loc[bad_created, 'CreatedDate'] = df.loc[bad_created, 'DateAdded']
                    df.loc[bad_created, 'CreatedDate_dt'] = df.loc[bad_created, 'DateAdded_dt']
                    date_fixes += bad_created.sum()
            if 'CreatedDate_dt' in df.columns and 'LastModified_dt' in df.columns:
                bad_modified = (df['LastModified_dt'] < df['CreatedDate_dt'])
                if bad_modified.any():
                    df.loc[bad_modified, 'LastModified'] = df.loc[bad_modified, 'CreatedDate']
                    date_fixes += bad_modified.sum()
            for col in date_cols_to_check:
                if f'{col}_dt' in df.columns:
                    df = df.drop(f'{col}_dt', axis=1)
            if date_fixes > 0:
                fixes_applied.append(f"Fixed date logic for {date_fixes} records")
        if fixes_applied:
            for fix in fixes_applied:
                print(f"   {fix}")
        return df
    def _generate_product_names_from_llm(self, count: int, subject: str) :
        print(f"   Generating {count} product names in batches...")
        unique_names = set()
        batch_size = 50
        max_attempts = max(5, (count // batch_size) * 3)
        attempts = 0
        while len(unique_names) < count and attempts < max_attempts:
            remaining = count - len(unique_names)
            current_batch_size = min(batch_size, remaining + 10)
            new_names = self._generate_product_batch_with_llm(
                current_batch_size, 
                subject, 
                unique_names
            )
            if not new_names:
                print("   LLM returned no names in batch, retrying...")
                attempts += 1
                continue
            initial_count = len(unique_names)
            unique_names.update(new_names)
            added = len(unique_names) - initial_count
            print(f"   Batch {attempts+1}: Added {added} unique names (Total: {len(unique_names)}/{count})")
            attempts += 1
            if added == 0 and attempts > 5:
                print("   No new names generated in recent batches, stopping early.")
                break
        final_names = list(unique_names)
        if len(final_names) < count and len(final_names) > 0:
            print(f"   Padding product list from {len(final_names)} to {count}...")
            while len(final_names) < count:
                final_names.extend(final_names)
            final_names = final_names[:count]
        return final_names
    def _generate_product_batch_with_llm(self, count: int, subject: str, existing_names: set) :
        exclusions = list(existing_names)[-20:] if existing_names else []
        exclusion_str = ", ".join(exclusions) if exclusions else "None"
        prompt = f"""Generate {count} unique product names for a '{subject}' product catalogue.
REQUIREMENTS:
- Each name must be DIFFERENT (no repetition)
- Names should be specific, descriptive, and commercially realistic
- Include brand/model/variant details when appropriate
- AVOID these names (recently generated): {exclusion_str}
- Return as JSON array: ["name1", "name2", ...]
Generate {count} unique product names:"""
        try:
            response = self.generate_with_llm(prompt, max_tokens=2000)
            cleaned_json = self.extract_json(response)
            if cleaned_json:
                try:
                    names = json.loads(cleaned_json)
                    if isinstance(names, list) and len(names) > 0:
                        return [str(n).strip() for n in names if n]
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"   LLM product batch generation failed: {e}")
        return []
    def _generate_company_names_from_llm(self, count: int, subject: str) :
        prompt = f"""Generate {count} unique company names for B2B customers in a '{subject}' context.
REQUIREMENTS:
- Each name must be DIFFERENT (no repetition)
- Names should sound professional and realistic (e.g., "Acme Corp", "Global Industries", "TechVision Systems")
- Mix of industries: manufacturing, technology, retail, healthcare, finance, logistics
- Include variety of company types: Corp, Inc, LLC, Industries, Solutions, Systems, Group
- Return as JSON array: ["name1", "name2", ...]
Generate {count} unique company names:"""
        try:
            response = self.generate_with_llm(prompt, max_tokens=1500, cache_key=f"company_names_{subject}_{count}")
            cleaned_json = self.extract_json(response)
            if cleaned_json:
                try:
                    names = json.loads(cleaned_json)
                    if isinstance(names, list) and len(names) > 0:
                        unique_names = list(dict.fromkeys([str(n).strip() for n in names if n]))
                        print(f"   LLM generated {len(unique_names)} company names")
                        return unique_names
                except json.JSONDecodeError:
                    print(f"   JSON parsing failed for company names")
        except Exception as e:
            print(f"   LLM company name generation failed: {e}")
        return []
    def _generate_categories_for_products(self, product_names: List[str], subject: str) :
        sample_size = min(len(product_names), 50)
        sample_products = product_names[:sample_size]
        prompt = f"""For each product below, assign an appropriate category. Return as a JSON object mapping product names to categories.
Products:
{json.dumps(sample_products, indent=2)}
REQUIREMENTS:
- Categories should match the product type (e.g., vinyl LPs → "Music", laptops → "Electronics", cosmetics → "Beauty")
- Use these category types: Electronics, Apparel, Music, Beauty, Home & Kitchen, Sports & Outdoors, Automotive, Books, Toys & Games
- Return as JSON object: {{"product_name": "category", ...}}
Generate category mappings:"""
        try:
            response = self.generate_with_llm(prompt, max_tokens=2000, cache_key=f"product_categories_{subject}_{len(product_names)}")
            cleaned_json = self.extract_json(response)
            if cleaned_json:
                try:
                    mapping = json.loads(cleaned_json)
                    if isinstance(mapping, dict) and len(mapping) > 0:
                        print(f"   LLM generated categories for {len(mapping)} products")
                        full_mapping = {}
                        for product in product_names:
                            if product in mapping:
                                full_mapping[product] = mapping[product]
                            else:
                                full_mapping[product] = self._guess_category_fallback(product)
                        return full_mapping
                except json.JSONDecodeError:
                    print(f"   JSON parsing failed for product categories")
        except Exception as e:
            print(f"   LLM product category generation failed: {e}")
        return {product: self._guess_category_fallback(product) for product in product_names}
    def _guess_category_fallback(self, product_name: str) :
        product_lower = product_name.lower()
        if any(word in product_lower for word in ['vinyl', 'lp', 'album', 'cd']):
            return "Music"
        elif any(word in product_lower for word in ['iphone', 'laptop', 'tv', 'camera', 'watch', 'tablet', 'mouse', 'keyboard', 'headphone', 'speaker']):
            return "Electronics"
        elif any(word in product_lower for word in ['jeans', 'shirt', 'shoe', 'jacket', 'brief', 'dress']):
            return "Apparel"
        elif any(word in product_lower for word in ['makeup', 'cosmetic', 'lipstick', 'foundation', 'mascara', 'lotion', 'cream', 'shampoo']):
            return "Beauty"
        elif any(word in product_lower for word in ['coffee', 'cookware', 'kitchen', 'mixer', 'vacuum', 'plug', 'bulb']):
            return "Home & Kitchen"
        elif any(word in product_lower for word in ['running', 'fitness', 'gym', 'sport']):
            return "Sports & Outdoors"
        elif any(word in product_lower for word in ['motor oil', 'brake', 'tire', 'car', 'auto']):
            return "Automotive"
        else:
            return "General Merchandise"
    def _generate_categories_from_llm(self, count: int, subject: str) :
        prompt = f"""Generate {count} product category assignments for a '{subject}' product catalogue.
REQUIREMENTS:
- Return a JSON array with {count} category names
- Use realistic product categories (e.g., Electronics, Apparel, Automotive, etc.)
- Distribute across multiple different categories
- Return as JSON array: ["category1", "category2", ...]
Generate {count} category assignments:"""
        try:
            response = self.generate_with_llm(prompt, max_tokens=1000, cache_key=f"categories_{subject}_{count}")
            cleaned_json = self.extract_json(response)
            if cleaned_json:
                try:
                    categories = json.loads(cleaned_json)
                    if isinstance(categories, list) and len(categories) > 0:
                        print(f"   LLM generated {len(categories)} categories")
                        return [str(c).strip() for c in categories if c]
                except json.JSONDecodeError:
                    print(f"   JSON parsing failed for categories")
        except Exception as e:
            print(f"   LLM category generation failed: {e}")
        return []
    def _generate_fallback_product_names(self, count: int) :
        CATEGORY_PRODUCTS = {
            'Electronics': [
                '4K Smart TV 55-inch', '4K Smart TV 65-inch', 'Wireless Noise-Canceling Headphones',
                'Digital Camera 24MP', 'Digital Camera 48MP Pro', 'Laptop 15-inch i7', 'Laptop 13-inch i5',
                'Bluetooth Speaker', 'USB-C Hub 7-in-1', 'Portable SSD 1TB', 'Portable SSD 2TB',
                'Mechanical Keyboard RGB', 'Gaming Mouse', 'USB-C Charging Cable 3-pack', 'Phone Screen Protector',
                'Wireless Mouse', 'Webcam 1080p', 'External Hard Drive 2TB', 'USB 3.0 Flash Drive 64GB',
                'Tablet 10-inch', 'Wireless Earbuds Pro', 'HDMI Cable 6-ft', 'DP to HDMI Adapter'
            ],
            'Automotive': [
                'Synthetic Motor Oil 5W-30', 'Synthetic Motor Oil 10W-40', 'Conventional Motor Oil 10W-30',
                'Brake Pad Set Front', 'Brake Pad Set Rear', 'Air Filter Standard', 'Air Filter High-Flow',
                'Cabin Air Filter', 'LED Headlight Bulbs H7', 'LED Headlight Bulbs H11', 'Windshield Wiper Blades 24-inch',
                'Windshield Wiper Blades 28-inch', 'Spark Plugs Set of 4', 'Battery 12V 100Ah', 'Floor Mats Set',
                'Car Air Freshener', 'Oil Filter', 'Coolant Antifreeze', 'Transmission Fluid', 'Tire Sealant'
            ],
            'Apparel': [
                "Men's Cotton T-Shirt White", "Men's Cotton T-Shirt Black", "Men's Cotton T-Shirt Navy",
                "Women's Running Shoes", "Women's Running Shoes Pro", 'Denim Jeans Blue', 'Denim Jeans Black',
                'Hoodie Sweatshirt Grey', 'Hoodie Sweatshirt Black', 'Athletic Shorts', 'Yoga Pants',
                "Men's Button-Up Shirt", "Women's Cardigan", 'Socks Crew 6-pack', 'Winter Beanie', 'Baseball Cap',
                'Leather Belt', 'Formal Dress Pants', "Women's Blazer", "Men's Polo Shirt"
            ],
            'Home Goods': [
                'Stainless Steel Cookware Set 10-piece', 'Stainless Steel Cookware Set 15-piece',
                'Memory Foam Pillow', 'Down Alternative Pillow', 'LED Desk Lamp Warm', 'LED Desk Lamp Cool White',
                'Coffee Maker 12-cup', 'Coffee Maker Single Serve', 'Vacuum Cleaner Upright', 'Vacuum Cleaner Robot',
                'Microwave Oven 1000W', 'Toaster 4-slice', 'Blender 1000W', 'Food Processor', 'Cutting Board Set',
                'Knife Block Set', 'Sheet Set Queen', 'Duvet Cover King', 'Throw Blanket'
            ],
            'Outdoor Gear': [
                'Camping Tent 2-Person', 'Camping Tent 4-Person', 'Camping Tent 6-Person', 'Hiking Backpack 50L',
                'Hiking Backpack 70L', 'Sleeping Bag Summer', 'Sleeping Bag Winter', 'Portable Camping Stove',
                'Camping Cooler 45L', 'Camping Cooler 70L', 'Water Bottle 1L', 'Water Bottle 2L Insulated',
                'Camping Pillow', 'Tent Footprint', 'Camping Headlamp', 'Multi-tool', 'Compass', 'Rope 50-ft',
                'Flashlight LED'
            ]
        }
        all_products = []
        for products in CATEGORY_PRODUCTS.values():
            all_products.extend(products)
        result = []
        for i in range(count):
            result.append(all_products[i % len(all_products)])
        random.shuffle(result)
        return result
    def generate_employee_data(self, rows: int, columns: int, subject: str) :
        print(f" Generating {rows} employee records with realistic hierarchy...")
        schema = [
            {'name': 'EmployeeID', 'type': 'id'},
            {'name': 'FirstName', 'type': 'text'},
            {'name': 'LastName', 'type': 'text'},
            {'name': 'Email', 'type': 'email'},
            {'name': 'Department', 'type': 'category'},
            {'name': 'JobTitle', 'type': 'text'},
            {'name': 'Manager', 'type': 'text'},
            {'name': 'HireDate', 'type': 'date'},
            {'name': 'Salary', 'type': 'money'},
            {'name': 'Status', 'type': 'category'},
            {'name': 'Country', 'type': 'category'},
            {'name': 'City', 'type': 'text'},
            {'name': 'PhoneNumber', 'type': 'phone'}
        ]
        employees = []
        batch_size = 50
        remaining = rows
        used_first_names = set()
        used_last_names = set()
        print(f"  Generating {rows} employees in batches of {batch_size} with name deduplication...")
        while remaining > 0:
            current_batch = min(batch_size, remaining)
            batch_data = self._generate_employee_batch_with_llm(
                current_batch,
                used_first_names,
                used_last_names
            )
            for emp in batch_data:
                if 'FirstName' in emp:
                    used_first_names.add(emp['FirstName'])
                if 'LastName' in emp:
                    used_last_names.add(emp['LastName'])
            employees.extend(batch_data)
            remaining -= len(batch_data)
            print(f"  - Generated {len(employees)}/{rows} employees")
            print(f"  - Unique first names so far: {len(used_first_names)}")
            print(f"  - Unique last names so far: {len(used_last_names)}")
        if not employees:
             print("   LLM employee generation failed completely, using procedural fallback")
             for _ in range(rows):
                first = random.choice(['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Jessica'])
                last = random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'])
                employees.append({
                    'FirstName': first,
                    'LastName': last,
                    'Department': random.choice(['Sales', 'Marketing', 'Engineering', 'HR', 'Finance']),
                    'JobTitle': 'Specialist'
                })
        employees = employees[:rows]
        while len(employees) < rows:
            first = random.choice(['John', 'Jane', 'Michael', 'Emily'])
            last = random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])
            employees.append({
                'FirstName': first,
                'LastName': last,
                'Department': 'General',
                'JobTitle': 'Staff'
            })
        print(f"  Post-processing: Ensuring 85-95 unique names...")
        target_min = int(rows * 0.85)
        target_max = int(rows * 0.95)
        first_count = len(used_first_names)
        last_count = len(used_last_names)
        max_regeneration_attempts = 100
        attempts = 0
        while (first_count < target_min or last_count < target_min) and attempts < max_regeneration_attempts:
            first_names = [e['FirstName'] for e in employees]
            last_names = [e['LastName'] for e in employees]
            from collections import Counter
            first_counts = Counter(first_names)
            last_counts = Counter(last_names)
            dup_indices = []
            for idx, emp in enumerate(employees):
                is_dup_first = first_counts[emp['FirstName']] > 1
                is_dup_last = last_counts[emp['LastName']] > 1
                if is_dup_first or is_dup_last:
                    dup_indices.append((idx, is_dup_first, is_dup_last))
            if not dup_indices:
                break
            idx, needs_new_first, needs_new_last = dup_indices[0]
            new_batch = self._generate_employee_batch_with_llm(1, used_first_names, used_last_names)
            if new_batch:
                new_emp = new_batch[0]
                if 'FirstName' in new_emp:
                    used_first_names.add(new_emp['FirstName'])
                if 'LastName' in new_emp:
                    used_last_names.add(new_emp['LastName'])
                employees[idx] = new_emp
                first_count = len(set(e['FirstName'] for e in employees))
                last_count = len(set(e['LastName'] for e in employees))
                print(f"  - Regenerated duplicate: First={first_count}, Last={last_count}")
            attempts += 1
        print(f"   Final diversity: {first_count} unique first names, {last_count} unique last names")
        df = pd.DataFrame(employees)
        df['EmployeeID'] = [self.generate_id_with_encoding('EMP', i) for i in range(rows)]
        countries = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France']
        df['Country'] = [random.choice(countries) for _ in range(rows)]
        df['City'] = df['Country'].apply(lambda c: random.choice(self._LOCATIONS.get(c, self._LOCATIONS['USA'])['cities']))
        df['Email'] = df.apply(lambda x: self.generate_email(x['FirstName'], x['LastName']), axis=1)
        df['PhoneNumber'] = df['Country'].apply(lambda c: self.generate_phone(c))
        now = datetime.now()
        df['HireDate'] = [(now - timedelta(days=random.randint(30, 365*10))).strftime('%Y-%m-%d') for _ in range(rows)]
        df['Status'] = random.choices(['Active', 'On Leave', 'Terminated'], weights=[0.9, 0.05, 0.05], k=rows)
        df['Salary'] = df.apply(lambda x: self.generate_salary(x['JobTitle'], x['Country'], x['Department']), axis=1)
        print("  Building manager hierarchy...")
        num_managers = max(1, int(rows * 0.15))
        manager_indices = random.sample(range(rows), num_managers)
        senior_titles = ['Manager', 'Director', 'VP', 'Team Lead', 'Head of']
        for idx in manager_indices:
            current_title = df.at[idx, 'JobTitle']
            if not any(t in current_title for t in senior_titles):
                df.at[idx, 'JobTitle'] = f"{current_title} {random.choice(senior_titles)}"
        num_execs = max(1, int(num_managers * 0.2))
        exec_indices = manager_indices[:num_execs]
        mid_manager_indices = manager_indices[num_execs:]
        managers = []
        for i in range(rows):
            if i in exec_indices:
                managers.append("Board of Directors")
            elif i in mid_manager_indices:
                mgr_idx = random.choice(exec_indices)
                managers.append(f"{df.at[mgr_idx, 'FirstName']} {df.at[mgr_idx, 'LastName']}")
            else:
                mgr_idx = random.choice(manager_indices)
                managers.append(f"{df.at[mgr_idx, 'FirstName']} {df.at[mgr_idx, 'LastName']}")
        df['Manager'] = managers
        print(f" Employee generation complete: {len(df)} rows")
        return df
    def _generate_employee_batch_with_llm(self, count = None, used_last_names: set = None) :
        used_first_names = used_first_names or set()
        used_last_names = used_last_names or set()
        first_exclusions = ", ".join(sorted(list(used_first_names))[:30]) if used_first_names else "none yet"
        last_exclusions = ", ".join(sorted(list(used_last_names))[:30]) if used_last_names else "none yet"
        prompt = f"""Generate {count} realistic employee profiles for a global company.
CRITICAL REQUIREMENTS:
- Return a JSON array of objects
- Each object must have: "FirstName", "LastName", "Department", "JobTitle"
- Names must be GLOBALLY DIVERSE (North American, European, Asian, Hispanic, African, Middle Eastern)
- NO DUPLICATE NAMES within this batch
- AVOID these first names already used: {first_exclusions}
- AVOID these last names already used: {last_exclusions}
- Departments (choose from these options):
  Engineering, Product Management, Sales, Marketing, Customer Success, Operations, Finance, Human Resources, IT / Infrastructure, Data Science, Design / UX, Quality Assurance, Legal, Research & Development, Security
- Job Titles: Vary by seniority (Junior, Senior, Manager, Director, VP) and match the department.
- JSON Format: [{{"FirstName": "Name", "LastName": "Name", "Department": "Dept", "JobTitle": "Title"}}, ...]
Generate {count} unique profiles:"""
        try:
            response = self.generate_with_llm(prompt, max_tokens=2000)
            cleaned_json = self.extract_json(response)
            if cleaned_json:
                data = json.loads(cleaned_json)
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"   LLM batch generation failed: {e}")
        return []
    def _generate_generic_data(self, rows: int, columns: int, subject: str, 
                               schema: List[Dict]) -> pd.DataFrame:
        print(f" Generating {rows} generic records via LLM")
        dataset = {}
        now = datetime.now()
        is_financial = 'financial' in subject.lower() and 'transaction' in subject.lower()
        if is_financial:
            merchant_names = [
                "Amazon", "Walmart", "Target", "Costco", "Best Buy",
                "Starbucks", "McDonald's", "Chipotle", "Whole Foods", "Trader Joe's",
                "Shell", "Chevron", "Exxon", "BP Gas Station", "7-Eleven",
                "CVS Pharmacy", "Walgreens", "Rite Aid", "Home Depot", "Lowe's",
                "Netflix", "Spotify", "Apple iTunes", "Google Play", "Amazon Prime",
                "Uber", "Lyft", "Delta Airlines", "United Airlines", "Marriott Hotels",
                "AT&T", "Verizon", "Comcast", "Electric Company", "Water Utility",
                "Bank Transfer", "Direct Deposit", "Payroll", "Insurance Payment", "Mortgage Payment"
            ]
        name_cols_exist = any('name' in c.get('name', '').lower() for c in schema)
        full_names = [self.generate_person_name() for _ in range(rows)] if name_cols_exist else None
        product_names_pool = []
        has_product_name = any('product' in c.get('name', '').lower() and 'name' in c.get('name', '').lower() for c in schema)
        if has_product_name:
            print("   Generating diverse product names via LLM...")
            product_count = min(rows, 100)
            product_names_pool = self._generate_product_names_from_llm(product_count, subject)
            if not product_names_pool:
                product_names_pool = self._generate_fallback_product_names(product_count)
        customer_names_pool = []
        has_customer_name = any('customer' in c.get('name', '').lower() and 'name' in c.get('name', '').lower() for c in schema)
        if has_customer_name:
            print("   Generating diverse customer names via LLM...")
            customer_count = min(max(rows // 3, 30), 60)
            customer_names_pool = self._generate_company_names_from_llm(customer_count, subject)
            if not customer_names_pool:
                customer_names_pool = [self.generate_company_name(subject) for _ in range(customer_count)]
        product_categories_map = {}
        has_category = any('category' in c.get('name', '').lower() for c in schema)
        if has_product_name and has_category and product_names_pool:
            print("    Generating matching categories for products via LLM...")
            product_categories_map = self._generate_categories_for_products(product_names_pool, subject)
        for col_schema in schema:
            col_name = col_schema.get('name', 'Field')
            col_type = col_schema.get('type', 'text')
            examples = col_schema.get('examples') or []
            col_data = []
            if col_type == 'id':
                prefix = re.sub(r'[^A-Z]', '', (col_name[:3].upper() or "ID"))
                col_data = [self.generate_id_with_encoding(prefix, i) for i in range(rows)]
            elif col_type == 'email':
                domain = "company.com"
                if full_names:
                    col_data = [f"{name.split()[0].lower()}.{name.split()[-1].lower()}@{domain}" for name in full_names]
                else:
                    col_data = [f"employee{i}@{domain}" for i in range(rows)]
            elif col_type in ('text', 'category'):
                if 'product' in col_name.lower() and 'name' in col_name.lower() and product_names_pool:
                    col_data = random.choices(product_names_pool, k=rows)
                elif 'category' in col_name.lower() and product_categories_map and 'product' not in col_name.lower():
                    product_col_name = next((c.get('name') for c in schema if 'product' in c.get('name', '').lower() and 'name' in c.get('name', '').lower()), None)
                    if product_col_name and product_col_name in dataset:
                        col_data = [product_categories_map.get(product, random.choice(list(product_categories_map.values()) or examples or ['Unknown'])) 
                                    for product in dataset[product_col_name]]
                    else:
                        col_data = random.choices(list(product_categories_map.values()) if product_categories_map else examples, k=rows)
                elif 'customer' in col_name.lower() and 'name' in col_name.lower() and customer_names_pool:
                    col_data = random.choices(customer_names_pool, k=rows)
                elif is_financial and 'merchant' in col_name.lower():
                    col_data = random.choices(merchant_names, k=rows)
                elif 'sales' in col_name.lower() and 'rep' in col_name.lower():
                    reps = [self.generate_person_name() for _ in range(random.randint(5, 10))]
                    col_data = random.choices(reps, k=rows)
                elif examples and len(examples) >= 1:
                    col_data = random.choices(examples, k=rows)
                else:
                    col_data = [f"{col_name}_{i+1}" for i in range(rows)]
            elif col_type == 'phone':
                col_data = [self.generate_phone() for _ in range(rows)]
            elif col_type == 'date':
                if is_financial and 'posted' in col_name.lower() and 'TransactionDate' in dataset:
                    col_data = []
                    for txn_date_str in dataset['TransactionDate']:
                        try:
                            txn_date = datetime.strptime(str(txn_date_str), "%Y-%m-%d")
                            posted_date = txn_date + timedelta(days=random.randint(0, 5))
                            col_data.append(posted_date.strftime("%Y-%m-%d"))
                        except:
                            col_data.append(self.generate_date())
                else:
                    col_data = [self.generate_date() for _ in range(rows)]
            elif col_type in ('int', 'integer', 'number'):
                if 'quantity' in col_name.lower():
                    col_data = [random.randint(1, 100) for _ in range(rows)]
                else:
                    col_data = [random.randint(1, 1000) for _ in range(rows)]
            elif col_type in ('float', 'money', 'price', 'currency'):
                if any(k in col_name.lower() for k in ['price', 'cost', 'amount', 'sale', 'total', 'balance']):
                    if is_financial and 'amount' in col_name.lower():
                        col_data = [round(random.paretovariate(1.5) * 50, 2) for _ in range(rows)]
                    else:
                        col_data = [round(random.uniform(10.0, 1000.0), 2) for _ in range(rows)]
                else:
                    col_data = [round(random.uniform(10.0, 1000.0), 2) for _ in range(rows)]
            elif any(k in col_name.lower() for k in ['price', 'cost', 'amount', 'sale', 'total']):
                 col_data = [round(random.uniform(10.0, 1000.0), 2) for _ in range(rows)]
            elif col_type == 'boolean':
                col_data = random.choices([True, False], weights=[0.8, 0.2], k=rows)
            elif col_type == 'percentage':
                col_data = [round(random.uniform(0, 100), 2) for _ in range(rows)]
            elif col_type == 'url':
                col_data = [f"https://example.com/{col_name.lower().replace(' ', '_')}/{i+1}" for i in range(rows)]
            else:
                col_data = [f"{col_name}_{i+1}" for i in range(rows)]
            if isinstance(col_data, list):
                col_data = [str(x).strip() if x is not None else x for x in col_data]
            dataset[col_name] = col_data
        if 'Quantity' in dataset and 'UnitPrice' in dataset:
            total_col = next((c for c in dataset.keys() if 'total' in c.lower() and 'sale' in c.lower()), None)
            if total_col:
                print("   Calculating TotalSale from Quantity * UnitPrice...")
                dataset[total_col] = [
                    round(float(q) * float(p), 2) 
                    for q, p in zip(dataset['Quantity'], dataset['UnitPrice'])
                ]
        df = pd.DataFrame(dataset)
        df = self._strip_whitespace_from_text(df)
        df = self._apply_category_standardization(df, [])
        df = self._validate_all_dates_in_past(df)
        df = self._apply_final_production_fixes(df, subject)
        try:
            _ = self.validate_data_quality_with_llm(df, subject)
        except Exception:
            pass
        print(f" Generation complete: {len(df)} rows × {len(df.columns)} columns")
        return df
    def generate_data_file(self, rows: int, columns: int, subject: str,
                           options = None, output_path: Optional[str] = None) -> str:
        options = options or {}
        fmt = options.get('format', 'xlsx').lower()
        df = self.generate_excel_data(rows, columns, subject, options)
        if not output_path:
            safe_subject = re.sub(r'[^0-9A-Za-z_-]', '_', subject) or "data"
            ext = 'xlsx' if fmt in ('xlsx', 'excel') else 'csv'
            output_path = os.path.join(tempfile.gettempdir(), f"{safe_subject}_{rows}x{columns}.{ext}")
        try:
            if fmt in ('xlsx', 'excel'):
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
            else:
                df.to_csv(output_path, index=False)
        except Exception:
            fallback_path = os.path.splitext(output_path)[0] + '.csv'
            df.to_csv(fallback_path, index=False)
            return fallback_path
        return output_path