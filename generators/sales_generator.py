"""Sales transaction generation functions.

This module provides specialized generation for sales transactions
including customer profiles, product pools, and realistic transaction patterns.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from .constants import LOCATIONS, PRODUCT_NAMES
from .llm_utils import extract_json, generate_with_llm
from .value_generators import generate_person_name


def generate_sales_transactions_with_entities(data_generator: Any, llm_cache: Dict[str, str],
                                             rows: int, columns: int, subject: str) -> pd.DataFrame:
    """Generate realistic sales transactions with entity relationships.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        rows: Number of transactions
        columns: Number of columns (unused)
        subject: Subject context
        
    Returns:
        DataFrame with sales transactions
    """
    print("=" * 80)
    print("GENERATING FINANCIAL TRANSACTIONS WITH ENTITY-BASED APPROACH")
    print("=" * 80)
    date_min = datetime(2020, 1, 1)
    date_max = datetime(2025, 11, 12)
    days_range = (date_max - date_min).days
    num_customers = random.randint(30, 40)
    print(f"Creating {num_customers} customers...")
    customers = []
    customer_profiles = _generate_customer_profiles_with_llm(data_generator, llm_cache, num_customers)
    if len(customer_profiles) < num_customers:
         while len(customer_profiles) < num_customers:
             customer_profiles.append(random.choice(customer_profiles))
    for i in range(num_customers):
        profile = customer_profiles[i]
        company_name = profile.get('name', f"Customer {i}")
        country = random.choice(list(LOCATIONS.keys()))
        city = random.choice(LOCATIONS[country]['cities'])
        max_creation_date = date_max - timedelta(days=90)
        creation_days_available = (max_creation_date - date_min).days
        created_days_offset = random.randint(0, creation_days_available)
        created_date = date_min + timedelta(days=created_days_offset)
        customers.append({
            'CustomerID': f"CUST-{1000+i}",
            'CustomerName': company_name,
            'Country': country,
            'City': city,
            'Region': random.choice(LOCATIONS[country]['states']),
            'CreatedDate': created_date
        })
    num_reps = random.randint(8, 12)
    print(f"Creating {num_reps} sales representatives...")
    sales_reps = [generate_person_name() for _ in range(num_reps)]
    for customer in customers:
        customer['PrimarySalesRep'] = random.choice(sales_reps)
    num_products = random.randint(50, 80)
    print(f"Creating {num_products} products...")
    product_pool = _generate_product_pool_with_llm(data_generator, llm_cache, num_products)
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


def _generate_customer_profiles_with_llm(data_generator: Any, llm_cache: Dict[str, str],
                                        count: int) -> List[Dict]:
    """Generate customer company profiles using LLM.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        count: Number of customer profiles
        
    Returns:
        List of customer profile dictionaries
    """
    print(f" LLM Prompt: Generating {count} customer profiles...")
    try:
        prompt = f"""Generate {count} unique and realistic B2B customer company names.
Include a mix of industries (Technology, Manufacturing, Healthcare, Finance, Retail).
Return a JSON object with a key "companies" containing a list of objects, each with:
- "name": The company name (creative, not just generic words)
- "industry": The industry sector
- "region_hint": A hint for location (e.g., "North America", "Europe", "Asia")
Ensure names are diverse and sound like real businesses.
Generate {count} companies:"""
        response = generate_with_llm(data_generator, llm_cache, prompt, 
                                   cache_key=f"customer_profiles_{count}", max_tokens=2000)
        cleaned_json = extract_json(response)
        if cleaned_json:
            data = json.loads(cleaned_json)
            if 'companies' in data and isinstance(data['companies'], list):
                print(f"LLM generated {len(data['companies'])} customer profiles")
                return data['companies'][:count]
    except Exception as e:
        print(f" LLM customer generation failed: {e}")
    fallback = []
    for i in range(count):
        fallback.append({
            'name': f"Company {i+1}",
            'industry': random.choice(['Technology', 'Manufacturing', 'Retail', 'Healthcare', 'Finance'])
        })
    return fallback


def _generate_product_pool_with_llm(data_generator: Any, llm_cache: Dict[str, str],
                                   count: int) -> List[Dict]:
    """Generate diverse product catalog using LLM.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        count: Number of products
        
    Returns:
        List of dicts with 'name', 'category', 'price'
    """
    prompt = f"""Generate {count} diverse products for a product catalog.
Return JSON with key "products" containing list of objects with:
- "name": Product name (specific and realistic)
- "category": Category (Electronics, Apparel, Home Goods, Outdoor Gear, Automotive)
- "price": Price as a number (realistic range 5.99 to 1999.99)
Generate {count} products:"""
    try:
        response = generate_with_llm(data_generator, llm_cache, prompt, 
                                   cache_key=f"product_pool_{count}", max_tokens=4000)
        cleaned_json = extract_json(response)
        if cleaned_json:
            data = json.loads(cleaned_json)
            if 'products' in data and isinstance(data['products'], list):
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


def _generate_company_names_from_llm(data_generator: Any, llm_cache: Dict[str, str],
                                    count: int, subject: str) -> List[str]:
    """Generate company names using LLM.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        count: Number of company names
        subject: Subject context
        
    Returns:
        List of company names
    """
    prompt = f"""Generate {count} unique company names for B2B customers in a '{subject}' context.
REQUIREMENTS:
- Each name must be DIFFERENT (no repetition)
- Names should sound professional and realistic (e.g., "Acme Corp", "Global Industries", "TechVision Systems")
- Mix of industries: manufacturing, technology, retail, healthcare, finance, logistics
- Include variety of company types: Corp, Inc, LLC, Industries, Solutions, Systems, Group
- Return as JSON array: ["name1", "name2", ...]
Generate {count} unique company names:"""
    try:
        response = generate_with_llm(data_generator, llm_cache, prompt, max_tokens=1500, 
                                   cache_key=f"company_names_{subject}_{count}")
        cleaned_json = extract_json(response)
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
