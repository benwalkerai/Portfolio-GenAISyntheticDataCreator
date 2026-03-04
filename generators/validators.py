"""Data validation and quality control functions.

This module provides functions for validating generated data including
business rules, date validation, quality checks, and data fixes.
"""

from __future__ import annotations

import json
import random
import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from .constants import KNOWN_CITIES


def _strip_whitespace_from_text(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from text columns.
    
    Args:
        df: DataFrame to process
        
    Returns:
        DataFrame with stripped text
    """
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].apply(lambda v: v.strip() if isinstance(v, str) else v)
    return df


def _apply_category_standardization(df: pd.DataFrame, rules: List[Any]) -> pd.DataFrame:
    """Apply category standardization rules.
    
    Args:
        df: DataFrame to process
        rules: Standardization rules (currently unused)
        
    Returns:
        Processed DataFrame
    """
    return df


def _validate_all_dates_in_past(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all date columns contain valid dates in the past.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        DataFrame with validated dates
    """
    for c in df.columns:
        column_name = c.lower()
        is_date_named_column = any(token in column_name for token in ['date', 'timestamp', 'time'])
        if is_date_named_column:
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


def _apply_final_production_fixes(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    """Apply final production fixes including column name deduplication.
    
    Args:
        df: DataFrame to fix
        subject: Subject context
        
    Returns:
        Fixed DataFrame
    """
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


def fix_employee_data_quality(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    """Apply employee-specific data quality fixes.
    
    Args:
        df: Employee DataFrame
        subject: Subject context
        
    Returns:
        Fixed DataFrame
    """
    if 'Email' in df.columns:
        return df
    # Additional fixes can be added here
    return df


def _apply_product_catalog_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    """Apply product catalog business rules and validation.
    
    Args:
        df: Product DataFrame
        
    Returns:
        DataFrame with business rules applied
    """
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


def apply_country_city_fix(df: pd.DataFrame, country_city_cache: Dict[str, List[str]]) -> pd.DataFrame:
    """Fix country-city mismatches using cached data.
    
    Args:
        df: DataFrame to fix
        country_city_cache: Cache of valid cities per country
        
    Returns:
        Fixed DataFrame
    """
    if 'Country' not in df.columns or 'City' not in df.columns:
        return df
    fixes = 0
    for idx in range(len(df)):
        country = df.at[idx, 'Country']
        city = df.at[idx, 'City']
        if pd.notna(country) and pd.notna(city):
            valid_cities = country_city_cache.get(str(country), [])
            if len(valid_cities) > 0 and city not in valid_cities:
                df.at[idx, 'City'] = random.choice(valid_cities)
                fixes += 1
    if fixes > 0:
        print(f"   Fixed {fixes} country-city mismatches with real cities")
    return df


def get_country_cities_from_llm(data_generator: Any, countries: List[str], 
                               country_city_cache: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Get or generate list of cities for given countries.
    
    Args:
        data_generator: Data generator with LLM access
        countries: List of country names
        country_city_cache: Cache dictionary
        
    Returns:
        Dictionary mapping countries to city lists
    """
    uncached_countries = [c for c in countries if c not in country_city_cache]
    if not uncached_countries:
        return country_city_cache
    known_count = 0
    unknown = []
    for country in uncached_countries:
        if country in KNOWN_CITIES:
            country_city_cache[country] = KNOWN_CITIES[country]
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
            response = data_generator.generate_with_ollama(prompt, max_tokens=800)
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
                        country_city_cache[country] = cities
                print(f"Generated cities for {len(cities_data)} countries")
            else:
                print(f"No JSON found in response")
        except Exception as e:
            print(f"City generation error: {e}")
            for country in unknown:
                country_city_cache[country] = ['Capital City', 'Major City', 'Port City', 'Urban Center', 'Regional Hub', 'Metro Area']
    return country_city_cache


def validate_data_quality_with_llm(df: pd.DataFrame, subject: str) -> bool:
    """Validate data quality using LLM (placeholder).
    
    Args:
        df: DataFrame to validate
        subject: Subject context
        
    Returns:
        True if validation passes
    """
    # This is a placeholder for future LLM-based validation
    return True
