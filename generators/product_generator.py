"""Product catalog generation functions.

This module provides specialized generation for product catalogs
including pricing, categories, inventory, and business rules.
"""

from __future__ import annotations

import json
import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Set

import pandas as pd

from .constants import CATEGORY_PRODUCTS, PRODUCT_CATALOG
from .llm_utils import extract_json, generate_with_llm
from .validators import _apply_product_catalog_business_rules, _apply_final_production_fixes, _strip_whitespace_from_text
from .value_generators import generate_company_name


def generate_product_catalog_with_llm(data_generator: Any, llm_cache: Dict[str, str],
                                     rows: int, columns: int, 
                                     subject: str, schema: List[Dict]) -> pd.DataFrame:
    """Generate product catalog with realistic business constraints.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        rows: Number of products
        columns: Number of columns (unused, uses predefined logic)
        subject: Subject context
        schema: Column schema
        
    Returns:
        DataFrame with product catalog
    """
    print(f" Generating {rows} products via LLM with STRICT realism constraints")
    print(" Requesting product names from LLM...")
    product_names = _generate_product_names_from_llm(data_generator, llm_cache, rows, subject)
    if not product_names or len(product_names) < rows:
        print(f"   LLM returned {len(product_names) if product_names else 0} names, using deterministic fallback")
        product_names = _generate_fallback_product_names(rows)
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
            product_lower = product_name.lower()
            # Apparel & Fashion (check first - very specific)
            if any(kw in product_lower for kw in ['shirt', 't-shirt', 'jeans', 'shoes', 'hoodie', 'shorts', 'pants', 'jacket', 'socks', 'hat', 'beanie', 'cap', 'blazer', 'cardigan', 'boots', 'sneakers', 'dress', 'skirt', 'sweater', 'coat', 'bra', 'wear', 'cloth']):
                categories_list.append('Apparel')
                assigned_products.append(product_name)
            # Automotive
            elif any(kw in product_lower for kw in ['motor oil', 'brake', 'spark plug', 'auto filter', 'car battery', 'wiper', 'transmission', 'coolant', 'tire', 'car wash', 'engine']):
                categories_list.append('Automotive')
                assigned_products.append(product_name)
            # Outdoor Gear (check before home goods)
            elif any(kw in product_lower for kw in ['tent', 'sleeping bag', 'camping', 'hiking', 'outdoor', 'stove', 'cooler', 'headlamp', 'compass', 'rope', 'footprint']):
                categories_list.append('Outdoor Gear')
                assigned_products.append(product_name)
            # Pet Supplies
            elif any(kw in product_lower for kw in ['dog', 'cat', 'pet', 'puppy', 'kitten', 'animal', 'paw', 'collar', 'leash']):
                categories_list.append('Pet Supplies')
                assigned_products.append(product_name)
            # Travel & Luggage (check before other categories)
            elif any(kw in product_lower for kw in ['travel', 'luggage', 'suitcase', 'packing', 'carry-on', 'duffel']):
                categories_list.append('Travel & Luggage')
                assigned_products.append(product_name)
            # Office & Furniture (check before home goods for desk/office items)
            elif any(kw in product_lower for kw in ['office chair', 'desk chair', 'ergonomic chair', 'office desk', 'filing cabinet', 'desk', 'pen', 'pencil', 'paper', 'notebook', 'folder', 'stapler', 'marker', 'highlighter']):
                categories_list.append('Office & Stationery')
                assigned_products.append(product_name)
            # Fitness & Sports (check mat vs mattress carefully)
            elif any(kw in product_lower for kw in ['yoga mat', 'fitness mat', 'exercise mat', 'yoga', 'fitness', 'exercise', 'workout', 'gym', 'athletic', 'sport', 'training', 'dumbbell', 'weight', 'tracker watch']):
                categories_list.append('Sports & Fitness')
                assigned_products.append(product_name)
            # Beauty & Personal Care
            elif any(kw in product_lower for kw in ['beauty', 'cosmetic', 'makeup', 'facial cleanser', 'skin', 'hair straightener', 'hydrating', 'glow', 'cream', 'serum', 'lotion']):
                categories_list.append('Beauty & Personal Care')
                assigned_products.append(product_name)
            # Home Appliances & Kitchen
            elif any(kw in product_lower for kw in ['vacuum', 'microwave', 'toaster', 'purifier', 'fan', 'heater', 'thermostat', 'humidifier', 'dehumidifier', 'washer', 'dryer', 'refrigerator', 'fridge', 'freezer', 'dishwasher', 'coffee maker', 'brew', 'water filter', 'filtration', 'blender', 'mixer', 'kitchen', 'cookware', 'chef', 'cook', 'bake', 'meal prep', 'knife', 'cutting board', 'pan', 'pot', 'grill', 'fryer', 'cooktop', 'culinary']):
                categories_list.append('Home Goods')
                assigned_products.append(product_name)
            # Home & Garden & Furniture
            elif any(kw in product_lower for kw in ['lamp', 'pillow', 'mattress', 'bedding', 'blanket', 'sheet', 'towel', 'rug', 'furniture', 'chair', 'garden', 'plant', 'soil', 'herb', 'seed', 'lights', 'solar', 'birdhouse', 'nest', 'aromatherapy', 'diffuser', 'candle']):
                categories_list.append('Home Goods')
                assigned_products.append(product_name)
            # Baby & Kids
            elif any(kw in product_lower for kw in ['baby', 'infant', 'toddler', 'child', 'kid', 'nursery', 'diaper', 'stroller', 'crib']):
                categories_list.append('Baby & Kids')
                assigned_products.append(product_name)
            # Electronics
            elif any(kw in product_lower for kw in ['smart', 'wireless', 'bluetooth', 'usb', 'charger', 'power bank', 'battery pack', 'camera', 'screen', 'display', 'speaker', 'headphone', 'earbuds', 'laptop', 'computer', 'phone', 'tablet', 'tv', 'monitor', 'remote', 'wifi', 'tech', 'digital', 'led', 'projector', 'keyboard', 'mouse', 'cable', 'adapter', 'router', 'hub', 'gaming', 'console', 'security camera']):
                categories_list.append('Electronics')
                assigned_products.append(product_name)
            # Everything else defaults to General Merchandise
            else:
                categories_list.append('General Merchandise')
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
            suppliers = [generate_company_name(subject) for _ in range(min(12, rows // 5))]
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
    df = _strip_whitespace_from_text(df)
    df = _apply_final_production_fixes(df, subject)
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
    df = _apply_product_catalog_business_rules(df)
    return df


def _generate_product_names_from_llm(data_generator: Any, llm_cache: Dict[str, str],
                                    count: int, subject: str) -> List[str]:
    """Generate product names using LLM in batches.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        count: Number of product names
        subject: Subject context
        
    Returns:
        List of product names
    """
    print(f"   Generating {count} product names in batches...")
    unique_names = set()
    batch_size = 50
    max_attempts = max(5, (count // batch_size) * 3)
    attempts = 0
    while len(unique_names) < count and attempts < max_attempts:
        remaining = count - len(unique_names)
        current_batch_size = min(batch_size, remaining + 10)
        new_names = _generate_product_batch_with_llm(
            data_generator, llm_cache,
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


def _generate_product_batch_with_llm(data_generator: Any, llm_cache: Dict[str, str],
                                     count: int, subject: str, 
                                     existing_names: Set[str]) -> List[str]:
    """Generate a batch of product names using LLM.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        count: Number of products
        subject: Subject context
        existing_names: Set of names to avoid
        
    Returns:
        List of product names
    """
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
        response = generate_with_llm(data_generator, llm_cache, prompt, max_tokens=2000)
        cleaned_json = extract_json(response)
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


def _generate_fallback_product_names(count: int) -> List[str]:
    """Generate fallback product names using deterministic method.
    
    Args:
        count: Number of product names needed
        
    Returns:
        List of product names
    """
    all_products = []
    for products in CATEGORY_PRODUCTS.values():
        all_products.extend(products)
    result = []
    for i in range(count):
        result.append(all_products[i % len(all_products)])
    random.shuffle(result)
    return result


def _generate_categories_for_products(data_generator: Any, llm_cache: Dict[str, str],
                                     product_names: List[str], subject: str) -> Dict[str, str]:
    """Generate category mappings for product names using LLM.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        product_names: List of product names
        subject: Subject context
        
    Returns:
        Dictionary mapping product names to categories
    """
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
        response = generate_with_llm(data_generator, llm_cache, prompt, max_tokens=2000, 
                                   cache_key=f"product_categories_{subject}_{len(product_names)}")
        cleaned_json = extract_json(response)
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
                            full_mapping[product] = _guess_category_fallback(product)
                    return full_mapping
            except json.JSONDecodeError:
                print(f"   JSON parsing failed for product categories")
    except Exception as e:
        print(f"   LLM product category generation failed: {e}")
    return {product: _guess_category_fallback(product) for product in product_names}


def _guess_category_fallback(product_name: str) -> str:
    """Guess product category based on keywords.
    
    Args:
        product_name: Product name
        
    Returns:
        Category name
    """
    product_lower = product_name.lower()
    # Pet Supplies
    if any(word in product_lower for word in ['dog', 'cat', 'pet', 'puppy', 'kitten', 'animal']):
        return "Pet Supplies"
    # Beauty & Personal Care
    elif any(word in product_lower for word in ['makeup', 'cosmetic', 'lipstick', 'foundation', 'mascara', 'lotion', 'cream', 'shampoo', 'beauty', 'facial', 'skin', 'hair', 'glow']):
        return "Beauty & Personal Care"
    # Sports & Fitness
    elif any(word in product_lower for word in ['yoga', 'fitness', 'exercise', 'workout', 'gym', 'athletic', 'sport', 'training', 'dumbbell', 'weight']):
        return "Sports & Fitness"
    # Electronics
    elif any(word in product_lower for word in ['iphone', 'laptop', 'tv', 'camera', 'watch', 'tablet', 'mouse', 'keyboard', 'headphone', 'speaker', 'smart', 'wireless', 'bluetooth', 'charger']):
        return "Electronics"
    # Apparel
    elif any(word in product_lower for word in ['jeans', 'shirt', 'shoe', 'jacket', 'brief', 'dress', 'socks', 'hat', 'pants', 'sweater']):
        return "Apparel"
    # Home Goods
    elif any(word in product_lower for word in ['coffee', 'cookware', 'kitchen', 'mixer', 'vacuum', 'plug', 'bulb', 'blanket', 'pillow', 'lamp', 'towel', 'rug', 'plant', 'garden', 'diffuser']):
        return "Home Goods"
    # Outdoor Gear
    elif any(word in product_lower for word in ['camping', 'hiking', 'outdoor', 'tent', 'backpack', 'sleeping bag']):
        return "Outdoor Gear"
    # Automotive
    elif any(word in product_lower for word in ['motor oil', 'brake', 'tire', 'car', 'auto', 'wiper', 'filter']):
        return "Automotive"
    # Travel & Luggage
    elif any(word in product_lower for word in ['travel', 'luggage', 'suitcase', 'packing', 'adapter', 'umbrella']):
        return "Travel & Luggage"
    # Office & Stationery
    elif any(word in product_lower for word in ['office', 'desk', 'pen', 'paper', 'notebook', 'marker', 'art', 'paint']):
        return "Office & Stationery"
    else:
        return "General Merchandise"


def _generate_categories_from_llm(data_generator: Any, llm_cache: Dict[str, str],
                                 count: int, subject: str) -> List[str]:
    """Generate category assignments using LLM.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        count: Number of categories
        subject: Subject context
        
    Returns:
        List of category names
    """
    prompt = f"""Generate {count} product category assignments for a '{subject}' product catalogue.
REQUIREMENTS:
- Return a JSON array with {count} category names
- Use realistic product categories (e.g., Electronics, Apparel, Automotive, etc.)
- Distribute across multiple different categories
- Return as JSON array: ["category1", "category2", ...]
Generate {count} category assignments:"""
    try:
        response = generate_with_llm(data_generator, llm_cache, prompt, max_tokens=1000, 
                                   cache_key=f"categories_{subject}_{count}")
        cleaned_json = extract_json(response)
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
