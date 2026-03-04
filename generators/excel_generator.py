"""Excel data generator orchestrator.

This module provides the main ExcelGenerator class that orchestrates
data generation by delegating to specialized generator modules.
"""

from __future__ import annotations

import os
import re
import tempfile
from typing import Any, Dict, List, Optional

import pandas as pd

from .constants import LOCATIONS
from . import employee_generator
from . import llm_utils
from . import product_generator
from . import sales_generator
from . import schema_templates
from . import validators
from . import value_generators


class ExcelGenerator:
    """Main orchestrator for Excel data generation.
    
    This class coordinates data generation by delegating to specialized
    modules for different data types and operations.
    """
    
    def __init__(self, data_generator: Any) -> None:
        """Initialize the Excel generator.
        
        Args:
            data_generator: Data generator instance with LLM access
        """
        self.data_generator = data_generator
        self.llm_cache: Dict[str, str] = {}
        self.domain_constraints: Dict = {}
        self._active_generation_options: Dict = {}
        self._country_city_cache: Dict[str, List[str]] = {}
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self.llm_cache.clear()
        if hasattr(self, '_country_city_cache'):
            self._country_city_cache.clear()
        print("ExcelGenerator cache cleared")
    
    def generate_excel_data(self, rows: int, columns: int, subject: str, 
                           options: Optional[Dict] = None) -> pd.DataFrame:
        """Generate Excel data based on subject and parameters.
        
        Args:
            rows: Number of rows to generate
            columns: Number of columns to generate
            subject: Subject/domain for data generation
            options: Optional generation options
            
        Returns:
            DataFrame with generated data
        """
        print(f" Starting generation for '{subject}' — {rows}×{columns}")
        schema = llm_utils.generate_column_headers_with_llm(
            self.data_generator, self.llm_cache, subject, columns,
            schema_templates._pad_schema, schema_templates.create_enhanced_fallback_schema
        )
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
                result_df = product_generator.generate_product_catalog_with_llm(
                    self.data_generator, self.llm_cache, rows, columns, subject, schema
                )
            else:
                is_employee = any(kw in subject_lower for kw in ['employee', 'staff', 'workforce', 'personnel', 'hr'])
                if is_employee:
                    print("Using specialized employee data generator")
                    result_df = employee_generator.generate_employee_data(
                        self.data_generator, self.llm_cache, rows, columns, subject
                    )
                else:
                    print("Using generic LLM-driven generator")
                    result_df = self._generate_generic_data(rows, columns, subject, schema)
        finally:
            self._active_generation_options = previous_options
        return result_df
    
    def generate_data_file(self, rows: int, columns: int, subject: str,
                           options: Optional[Dict] = None, 
                           output_path: Optional[str] = None) -> str:
        """Generate data and save to file.
        
        Args:
            rows: Number of rows
            columns: Number of columns
            subject: Subject/domain
            options: Optional generation options
            output_path: Optional output file path
            
        Returns:
            Path to generated file
        """
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
    
    def _generate_generic_data(self, rows: int, columns: int, subject: str, 
                               schema: List[Dict]) -> pd.DataFrame:
        """Generate generic data for any subject.
        
        Args:
            rows: Number of rows
            columns: Number of columns
            subject: Subject context
            schema: Column schema
            
        Returns:
            DataFrame with generated data
        """
        print(f" Generating {rows} generic records via LLM")
        dataset = {}
        from datetime import datetime, timedelta
        import random
        now = datetime.now()
        is_financial = 'financial' in subject.lower() and 'transaction' in subject.lower()
        
        # For financial transactions, create correlated merchant-category-type data
        financial_transaction_data = {}
        if is_financial:
            from .constants import FINANCIAL_MERCHANTS
            
            # Generate all financial transaction records with proper correlations
            all_categories = list(FINANCIAL_MERCHANTS.keys())
            category_weights = [2, 2, 3, 2, 2, 3, 1, 2, 1, 1, 1, 1]  # Adjust frequency of each category
            
            financial_transaction_data['categories'] = random.choices(
                all_categories, 
                weights=category_weights[:len(all_categories)],
                k=rows
            )
            
            # Generate merchants based on their categories
            financial_transaction_data['merchants'] = []
            financial_transaction_data['transaction_types'] = []
            financial_transaction_data['amounts'] = []
            
            for category in financial_transaction_data['categories']:
                category_data = FINANCIAL_MERCHANTS[category]
                merchant = random.choice(category_data['merchants'])
                txn_type = random.choice(category_data['transaction_types'])
                min_amt, max_amt = category_data['amount_range']
                
                # Generate amount with realistic distribution
                if category == 'Income':
                    # Salaries tend to be consistent amounts
                    amount = round(random.uniform(min_amt, max_amt), 2)
                elif category_data.get('recurring', False):
                    # Recurring payments have less variation
                    base_amount = random.uniform(min_amt, max_amt)
                    amount = round(base_amount + random.uniform(-base_amount*0.05, base_amount*0.05), 2)
                else:
                    # One-time purchases have more variation
                    amount = round(random.uniform(min_amt, max_amt), 2)
                
                financial_transaction_data['merchants'].append(merchant)
                financial_transaction_data['transaction_types'].append(txn_type)
                financial_transaction_data['amounts'].append(amount)
            
        
        name_cols_exist = any('name' in c.get('name', '').lower() for c in schema)
        full_names = [value_generators.generate_person_name() for _ in range(rows)] if name_cols_exist else None
        product_names_pool = []
        has_product_name = any('product' in c.get('name', '').lower() and 'name' in c.get('name', '').lower() for c in schema)
        if has_product_name:
            print("   Generating diverse product names via LLM...")
            product_count = min(rows, 100)
            product_names_pool = product_generator._generate_product_names_from_llm(
                self.data_generator, self.llm_cache, product_count, subject
            )
            if not product_names_pool:
                product_names_pool = product_generator._generate_fallback_product_names(product_count)
        customer_names_pool = []
        has_customer_name = any('customer' in c.get('name', '').lower() and 'name' in c.get('name', '').lower() for c in schema)
        if has_customer_name:
            print("   Generating diverse customer names via LLM...")
            customer_count = min(max(rows // 3, 30), 60)
            customer_names_pool = sales_generator._generate_company_names_from_llm(
                self.data_generator, self.llm_cache, customer_count, subject
            )
            if not customer_names_pool:
                customer_names_pool = [value_generators.generate_company_name(subject) for _ in range(customer_count)]
        product_categories_map = {}
        has_category = any('category' in c.get('name', '').lower() for c in schema)
        if has_product_name and has_category and product_names_pool:
            print("    Generating matching categories for products via LLM...")
            product_categories_map = product_generator._generate_categories_for_products(
                self.data_generator, self.llm_cache, product_names_pool, subject
            )
        for col_schema in schema:
            col_name = col_schema.get('name', 'Field')
            col_type = col_schema.get('type', 'text')
            examples = col_schema.get('examples') or []
            col_data = []
            if col_type == 'id':
                prefix = re.sub(r'[^A-Z]', '', (col_name[:3].upper() or "ID"))
                col_data = [value_generators.generate_id_with_encoding(prefix, i) for i in range(rows)]
            elif col_type == 'email':
                domain = "company.com"
                if full_names:
                    col_data = [f"{name.split()[0].lower()}.{name.split()[-1].lower()}@{domain}" for name in full_names]
                else:
                    col_data = [f"employee{i}@{domain}" for i in range(rows)]
            elif col_type in ('text', 'category'):
                if 'product' in col_name.lower() and 'name' in col_name.lower() and product_names_pool:
                    col_data = random.choices(product_names_pool, k=rows)
                elif 'category' in col_name.lower() and 'product' not in col_name.lower():
                    # Check if this is a financial transaction category FIRST
                    if is_financial and financial_transaction_data:
                        col_data = financial_transaction_data['categories']
                    elif product_categories_map:
                        product_col_name = next((c.get('name') for c in schema if 'product' in c.get('name', '').lower() and 'name' in c.get('name', '').lower()), None)
                        if product_col_name and product_col_name in dataset:
                            col_data = [product_categories_map.get(product, random.choice(list(product_categories_map.values()) or examples or ['Unknown'])) 
                                        for product in dataset[product_col_name]]
                        else:
                            col_data = random.choices(list(product_categories_map.values()) if product_categories_map else examples, k=rows)
                    elif examples:
                        col_data = random.choices(examples, k=rows)
                    else:
                        col_data = [f"{col_name}_{i+1}" for i in range(rows)]
                elif 'customer' in col_name.lower() and 'name' in col_name.lower() and customer_names_pool:
                    col_data = random.choices(customer_names_pool, k=rows)
                elif is_financial and 'merchant' in col_name.lower() and 'merchants' in financial_transaction_data:
                    col_data = financial_transaction_data['merchants']
                elif is_financial and 'transaction' in col_name.lower() and 'type' in col_name.lower() and 'transaction_types' in financial_transaction_data:
                    col_data = financial_transaction_data['transaction_types']
                elif is_financial and 'description' in col_name.lower() and 'categories' in financial_transaction_data:
                    # Generate realistic descriptions based on merchant/category
                    col_data = []
                    merchant_col = dataset.get('MerchantName', [''] * rows)
                    category_col = financial_transaction_data.get('categories', [''] * rows)
                    for merchant, category in zip(merchant_col, category_col):
                        if category == 'Housing':
                            desc = f"Monthly {category.lower()} payment"
                        elif category == 'Utilities':
                            desc = f"{category} bill payment"
                        elif category == 'Income':
                            desc = f"Payroll direct deposit"
                        elif category == 'Insurance':
                            desc = f"Monthly insurance premium"
                        elif category == 'Transfers':
                            desc = f"Account transfer"
                        else:
                            desc = f"Purchase at {merchant}" if merchant else f"{category} purchase"
                        col_data.append(desc)
                elif is_financial and 'status' in col_name.lower():
                    # Most transactions should be Posted, with some Pending
                    col_data = random.choices(['Posted', 'Pending', 'Cleared'], weights=[0.7, 0.2, 0.1], k=rows)
                elif is_financial and 'note' in col_name.lower() and 'categories' in financial_transaction_data:
                    # Add notes for recurring transactions
                    col_data = []
                    from .constants import FINANCIAL_MERCHANTS
                    category_col = financial_transaction_data.get('categories', [''] * rows)
                    for category in category_col:
                        if category in FINANCIAL_MERCHANTS and FINANCIAL_MERCHANTS[category].get('recurring', False):
                            col_data.append(random.choice(['Recurring monthly', 'Auto-payment', '']))
                        else:
                            col_data.append('')
                elif 'sales' in col_name.lower() and 'rep' in col_name.lower():
                    reps = [value_generators.generate_person_name() for _ in range(random.randint(5, 10))]
                    col_data = random.choices(reps, k=rows)
                elif examples and len(examples) >= 1:
                    col_data = random.choices(examples, k=rows)
                else:
                    col_data = [f"{col_name}_{i+1}" for i in range(rows)]
            elif col_type == 'phone':
                col_data = [value_generators.generate_phone() for _ in range(rows)]
            elif col_type == 'date':
                if is_financial and 'posted' in col_name.lower() and 'TransactionDate' in dataset:
                    col_data = []
                    for txn_date_str in dataset['TransactionDate']:
                        try:
                            from datetime import datetime
                            txn_date = datetime.strptime(str(txn_date_str), "%Y-%m-%d")
                            posted_date = txn_date + timedelta(days=random.randint(0, 5))
                            col_data.append(posted_date.strftime("%Y-%m-%d"))
                        except:
                            col_data.append(value_generators.generate_date(active_options=self._active_generation_options))
                else:
                    col_data = [value_generators.generate_date(active_options=self._active_generation_options) for _ in range(rows)]
            elif col_type in ('int', 'integer', 'number'):
                if 'quantity' in col_name.lower():
                    col_data = [random.randint(1, 100) for _ in range(rows)]
                else:
                    col_data = [random.randint(1, 1000) for _ in range(rows)]
            elif col_type in ('float', 'money', 'price', 'currency'):
                if any(k in col_name.lower() for k in ['price', 'cost', 'amount', 'sale', 'total', 'balance']):
                    if is_financial and 'amount' in col_name.lower() and 'amounts' in financial_transaction_data:
                        # Use the pre-generated correlated amounts for financial transactions
                        col_data = financial_transaction_data['amounts']
                    elif is_financial and 'balance' in col_name.lower():
                        # Generate running balance if amount column exists
                        if 'Amount' in dataset:
                            starting_balance = round(random.uniform(5000, 50000), 2)
                            col_data = []
                            current_balance = starting_balance
                            for i, amount in enumerate(dataset['Amount']):
                                # Adjust balance based on transaction type
                                txn_type = dataset.get('TransactionType', [None]*rows)[i] if 'TransactionType' in dataset else None
                                if txn_type in ['Deposit', 'Credit', 'Income']:
                                    current_balance += float(amount)
                                else:
                                    current_balance -= float(amount)
                                col_data.append(round(current_balance, 2))
                        else:
                            col_data = [round(random.uniform(1000.0, 50000.0), 2) for _ in range(rows)]
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
        df = validators._strip_whitespace_from_text(df)
        df = validators._apply_category_standardization(df, [])
        df = validators._validate_all_dates_in_past(df)
        df = validators._apply_final_production_fixes(df, subject)
        try:
            _ = validators.validate_data_quality_with_llm(df, subject)
        except Exception:
            pass
        print(f" Generation complete: {len(df)} rows × {len(df.columns)} columns")
        return df
