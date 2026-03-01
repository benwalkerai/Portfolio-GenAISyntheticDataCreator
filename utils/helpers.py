import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import gradio as gr

from config.settings import file_format_options

CAT_PREFIX = {
    "Electronics": "ELE",
    "Outdoor Gear": "OUT",
    "Automotive": "AUT",
    "Home Goods": "HOM",
    "Apparel": "APP",
    "Sports": "SPR",
}

CATEGORY_CONFIG = {
    "Electronics": {"price_range": (50, 2000), "cost_ratio": (0.7, 0.8), "reorder": (5, 15)},
    "Outdoor Gear": {"price_range": (25, 600), "cost_ratio": (0.7, 0.8), "reorder": (5, 15)},
    "Automotive": {"price_range": (20, 800), "cost_ratio": (0.7, 0.8), "reorder": (15, 50)},
    "Home Goods": {"price_range": (15, 1500), "cost_ratio": (0.7, 0.8), "reorder": (15, 50)},
    "Apparel": {"price_range": (10, 300), "cost_ratio": (0.7, 0.8), "reorder": (10, 30)},
    "Sports": {"price_range": (10, 600), "cost_ratio": (0.7, 0.8), "reorder": (10, 30)},
}

CATEGORY_NAME_KEYWORDS = {
    "Automotive": ["Wiper", "Brake", "Drive", "Torque", "Pad", "Blade"],
    "Electronics": ["Headphones", "Camera", "Charger", "Speaker", "Wireless", "USB", "Bluetooth"],
    "Outdoor Gear": ["Backpack", "Tent", "Headlamp", "Bottle", "Summit", "Trail"],
    "Home Goods": ["Comforter", "Knife", "Coffee", "Thermostat", "Brew", "Kitchen"],
    "Apparel": ["Sneakers", "Hoodie", "Socks", "Jacket", "Thermal"],
    "Sports": ["Racket", "Yoga", "Mat", "Gloves", "Bike"],
}

VARIANTS = ["Black", "White", "Red", "Blue", "Green", "64GB", "128GB", "XL", "L", "M", "2024 Edition", "50L", "70L"]

def _make_unique_names(base_pool, count):
    
    names = []
    attempts = 0
    descriptors = [
        "Series", "Pro", "Max", "Lite", "Plus", "Edition", "Hybrid", "Advanced",
        "Compact", "Deluxe", "Sport", "Elite", "Classic"
    ]
    while len(names) < count:
        base = random.choice(base_pool)
        variant = random.choice(VARIANTS)
        descriptor = random.choice(descriptors)
        model = f"{random.randint(100,999)}"
        patterns = [
            f"{base} {descriptor} {variant} - Model {model}",
            f"{descriptor} {base} - {variant} ({model})",
            f"{base} - {variant} - {descriptor} {model}",
            f"{base} {variant} {model}"
        ]
        name = random.choice(patterns)
        if name not in names:
            names.append(name)
        attempts += 1
        if attempts > count * 25:
            while len(names) < count:
                base = random.choice(base_pool)
                names.append(f"{base} - {uuid.uuid4().hex[:6]}")
    return names[:count]

def _productid_with_gaps(
    n,
    start=341000,
    end=342000,
    gap_pct_range=(0.10, 0.15),
):
    
    seq = list(range(start, end+1))
    gap_pct = random.uniform(*gap_pct_range)
    drop_n = int(len(seq) * gap_pct)
    if drop_n > 0:
        drop_indices = set(np.random.choice(len(seq), size=drop_n, replace=False))
        seq = [v for i,v in enumerate(seq) if i not in drop_indices]
    seq = seq[:n]
    while len(seq) < n:
        seq.append(seq[-1] + random.randint(2,10))
    return [f"PRO-{v}" for v in seq]

def _unique_skus(categories):
    
    skus = []
    used = set()
    for cat in categories:
        prefix = CAT_PREFIX.get(cat, "GEN")
        attempt = 0
        while True:
            candidate = f"{prefix}-{random.randint(1000,9999)}"
            if candidate in used:
                candidate = f"{candidate}-{random.choice(['BLK','RED','GRN','XL','64G'])}"
            if candidate not in used:
                used.add(candidate)
                skus.append(candidate)
                break
            attempt += 1
            if attempt > 30:
                fallback = f"{prefix}-{uuid.uuid4().hex[:6]}"
                used.add(fallback)
                skus.append(fallback)
                break
    if len(set(skus)) != len(skus):
        for i,s in enumerate(skus):
            if skus.count(s) > 1:
                skus[i] = f"{s}-{uuid.uuid4().hex[:4]}"
    return skus

def _stock_quantities(n):
    
    stock = np.random.lognormal(mean=2.5, sigma=1.0, size=n).astype(int)
    stock = np.clip(stock, 0, 500)
    zero_count = max(1, int(0.05 * n))
    zero_idx = np.random.choice(n, size=zero_count, replace=False)
    stock[zero_idx] = 0
    return stock

def _price_and_cost(categories):
    
    prices = []
    costs = []
    for cat in categories:
        cfg = CATEGORY_CONFIG.get(cat, {})
        pmin, pmax = cfg.get("price_range", (5,500))
        pmin = max(5.99, pmin)
        pmax = min(2999.99, pmax)
        price = round(np.random.uniform(pmin, pmax), 2)
        cost = round(price * np.random.uniform(0.70, 0.80), 2)
        if cost >= price:
            cost = round(price * 0.7, 2)
        prices.append(price)
        costs.append(cost)
    return prices, costs

def _reorder_levels(categories):
    
    rl = []
    for cat in categories:
        cfg = CATEGORY_CONFIG.get(cat, {})
        lo, hi = cfg.get("reorder", (10,30))
        lo = max(5, lo)
        hi = min(50, hi)
        rl.append(int(random.randint(lo, hi)))
    return rl

def verify_dataframe(df):
    
    msgs = []
    required = ["ProductID","ProductName","SKU","Category","Price","Cost","DateAdded","CreatedDate"]
    nulls = df[required].isnull().sum().sum()
    if nulls > 0:
        msgs.append(f"{nulls} required-field nulls")
    if not df["SKU"].is_unique:
        msgs.append("SKU not unique")
    if not (pd.to_datetime(df["LastModified"]) >= pd.to_datetime(df["DateAdded"])).all():
        msgs.append("LastModified < DateAdded for some rows")
    if not (df["Price"] > df["Cost"]).all():
        msgs.append("Some Price <= Cost")
    if not pd.api.types.is_integer_dtype(df["ReorderLevel"]):
        msgs.append("ReorderLevel not integer")
    try:
        if df["StockQuantity"].median() <= 10:
            msgs.append("StockQuantity median <= 10")
    except Exception:
        msgs.append("StockQuantity check failed")
    return (len(msgs)==0, msgs)

def generate_product_catalog(
    n,
    file_format="csv",
    seed=None,
):
    
    if seed is None:
        import time
        seed = int(time.time() * 1000) % (2**32)

    random.seed(seed)
    np.random.seed(seed)
    categories = list(CATEGORY_CONFIG.keys())
    cat_probs = np.array([0.20,0.15,0.15,0.20,0.20,0.10])
    cat_probs = cat_probs / cat_probs.sum()
    assigned = list(np.random.choice(categories, size=n, p=cat_probs))

    base_pools = {
        "Electronics": ["Acoustic Go Headphones","Nova Action Cam","Pulse Wireless Charger","Hydro Smart Speaker"],
        "Outdoor Gear": ["Summit Backpack","Trek Tent","Lumen Headlamp","Trail Water Bottle"],
        "Automotive": ["Hydro 28-inch Wiper Blade","Torque Brake Pad","Drive Belt"],
        "Home Goods": ["Comforter Set","Chef Knife","Brew Coffee Maker","Smart Thermostat"],
        "Apparel": ["Sport Running Sneakers","Comfy Hoodie","Thermal Socks"],
        "Sports": ["Pro Tennis Racket","Elite Yoga Mat","Performance Bike Gloves"]
    }

    cat_to_names = {}
    for c in categories:
        cnt = assigned.count(c)
        pool = base_pools.get(c, [f"{c} Product"])
        cat_to_names[c] = _make_unique_names(pool, cnt)

    product_ids = _productid_with_gaps(n, start=341000, end=342000, gap_pct_range=(0.10,0.15))
    skus = _unique_skus(assigned)
    prices, costs = _price_and_cost(assigned)
    stock = _stock_quantities(n)
    reorder = _reorder_levels(assigned)

    min_date = datetime(2020, 1, 1).date()
    max_date = datetime(2025, 11, 12).date()
    total_days = (max_date - min_date).days
    bias = np.random.beta(2.0, 1.0, size=n)
    DateAdded = [min_date + timedelta(days=int(b * total_days)) for b in bias]
    CreatedDate = []
    for d in DateAdded:
        add_days = random.randint(0, 30)
        cd = d + timedelta(days=add_days)
        if cd > max_date:
            cd = max_date
        CreatedDate.append(cd)
    LastModified = []
    for cd in CreatedDate:
        add_days = random.randint(0, 365)
        lm = cd + timedelta(days=add_days)
        if lm > max_date:
            lm = max_date
        LastModified.append(lm)

    suppliers = ["Acme Supplies","Prime Components","Global Distributors","Local Sourcing Co.","Niche Makers"]
    weights = np.array([0.30,0.18,0.12,0.10,0.30]); weights = weights/weights.sum()
    Supplier = list(np.random.choice(suppliers, size=n, p=weights))
    miss_idx = np.random.choice(n, size=max(1,int(0.03*n)), replace=False)
    for i in miss_idx:
        Supplier[i] = None

    product_names = []
    cursors = {c:0 for c in categories}
    for cat in assigned:
        idx = cursors[cat]
        name = cat_to_names[cat][idx]
        product_names.append(name)
        cursors[cat] += 1

    df = pd.DataFrame({
        "ProductID": product_ids,
        "ProductName": product_names,
        "SKU": skus,
        "Category": assigned,
        "Price": prices,
        "Cost": costs,
        "StockQuantity": stock,
        "ReorderLevel": reorder,
        "Supplier": Supplier,
        "DateAdded": DateAdded,
        "CreatedDate": CreatedDate,
        "LastModified": LastModified,
    })

    required = ["ProductID","ProductName","SKU","Category","Price","Cost","DateAdded","CreatedDate"]
    for col in required:
        if df[col].isnull().any():
            if df[col].dtype == object:
                df[col] = df[col].fillna("UNKNOWN")
            else:
                if col in ("Price", "Cost"):
                    df[col] = df[col].fillna(9.99)
                else:
                    df[col] = df[col].fillna(0)

    df["ReorderLevel"] = df["ReorderLevel"].astype(pd.Int64Dtype())
    df["StockQuantity"] = df["StockQuantity"].astype(int)
    df["Price"] = df["Price"].astype(float)
    df["Cost"] = df["Cost"].astype(float)

    df["Price"] = df["Price"].clip(lower=5.99, upper=2999.99)
    df["Cost"] = df["Cost"].clip(lower=0.0)
    df["StockQuantity"] = df["StockQuantity"].clip(lower=0, upper=500).astype(int)

    if not df["SKU"].is_unique:
        used = set()
        new_skus = []
        for i,cat in enumerate(df["Category"].tolist()):
            prefix = CAT_PREFIX.get(cat, "GEN")
            attempts = 0
            while True:
                candidate = f"{prefix}-{random.randint(1000,9999)}"
                if candidate not in used:
                    used.add(candidate); new_skus.append(candidate); break
                attempts += 1
                if attempts > 50:
                    fallback = f"{prefix}-{uuid.uuid4().hex[:6]}"
                    used.add(fallback); new_skus.append(fallback); break
        df["SKU"] = new_skus

    da = pd.to_datetime(df["DateAdded"]); lm = pd.to_datetime(df["LastModified"])
    bad = lm < da
    if bad.any():
        df.loc[bad, "LastModified"] = df.loc[bad, "DateAdded"]

    price_le_cost = df["Price"] <= df["Cost"]
    for i in df[price_le_cost].index:
        cat = df.at[i, "Category"]
        cr_min, cr_max = CATEGORY_CONFIG.get(cat, {}).get("cost_ratio", (0.3,0.8))
        df.at[i, "Cost"] = round(df.at[i, "Price"] * random.uniform(cr_min, cr_max), 2)
        if df.at[i, "Cost"] >= df.at[i, "Price"]:
            df.at[i, "Cost"] = round(df.at[i, "Price"] * 0.6, 2)

    for i in df.index:
        cat = df.at[i, "Category"]; name = df.at[i, "ProductName"]
        keywords = CATEGORY_NAME_KEYWORDS.get(cat, [])
        if keywords and not any(k.lower() in name.lower() for k in keywords):
            df.at[i, "ProductName"] = f"{name} ({cat})"

    valid, msgs = verify_dataframe(df)
    status = "OK" if valid else "Generated with issues: " + "; ".join(msgs)

    fname = f"synthetic_product_catalog_{uuid.uuid4().hex[:8]}"
    out_dir = tempfile.gettempdir()
    if str(file_format).lower().endswith(".xlsx") or str(file_format).lower() == "xlsx":
        out_path = os.path.join(out_dir, fname + ".xlsx")
        df.to_excel(out_path, index=False)
    else:
        out_path = os.path.join(out_dir, fname + ".csv")
        df.to_csv(out_path, index=False)

    preview = df.head(10)
    return out_path, f"{status} — saved to {out_path}", preview


def update_options(file_format):
    
    config = file_format_options.get(file_format, {})
    uses_dropdowns = bool(config.get("uses_dropdowns", False))

    if uses_dropdowns:
        size_update = gr.update(
            label=config.get("size_label", "Number of Pages"),
            value=config.get("size_default", 1),
            minimum=1,
            maximum=config.get("size_max", 50),
            visible=True,
        )
        content_options = config.get("content_options", [])
        if content_options:
            content_update = gr.update(
                choices=content_options,
                label=config.get("content_label", "Content"),
                value=content_options[0],
                visible=True,
            )
        else:
            content_update = gr.update(
                label=config.get("content_label", "Content"),
                value=config.get("content_default", None),
                visible=True,
            )
    else:
        size_update = gr.update(
            label=config.get("size_label", "Number of Rows"),
            value=config.get("size_default", 100),
            minimum=1,
            maximum=config.get("size_max", 100000),
            visible=True,
        )
        content_update = gr.update(
            label=config.get("content_label", "Number of Columns"),
            value=config.get("content_default", 10),
            minimum=1,
            maximum=config.get("content_max", 100),
            visible=True,
        )

    return size_update, content_update

def generate_synthetic_data(
    file_format,
    size_value,
    content_value,
    subject_input,
    enforce_correlations=True,
    prevent_future=True,
    apply_distributions=True,
    add_missingness=False,
    missingness_rate=0.0,
    add_noise=False,
    noise_level=0.0,
):
    
    try:
        if file_format in ["Excel Spreadsheet (.xlsx)", "CSV File (.csv)"]:
            rows = int(size_value) if size_value is not None else 100
            cols = int(content_value) if content_value is not None else 10

            from generators.data_generator import SyntheticDataGenerator
            generator = SyntheticDataGenerator()
            if hasattr(generator, 'excel_generator') and hasattr(generator.excel_generator, 'clear_cache'):
                generator.excel_generator.clear_cache()
            path, msg, preview = generator.generate_data_file(
                rows, cols, subject_input, file_format,
                {
                    "enforce_correlations": bool(enforce_correlations),
                    "prevent_future": bool(prevent_future),
                    "apply_distributions": bool(apply_distributions),
                    "add_missingness": bool(add_missingness),
                    "missingness_rate": float(missingness_rate or 0.0),
                    "add_noise": bool(add_noise),
                    "noise_level": float(noise_level or 0.0),
                }
            )
            return path, msg, preview
        elif file_format in ["Word Document (.docx)", "PDF Document (.pdf)", "Text File (.txt)"]:
            from generators.data_generator import SyntheticDataGenerator
            generator = SyntheticDataGenerator()
            if hasattr(generator, 'document_generator') and hasattr(generator.document_generator, 'clear_cache'):
                generator.document_generator.clear_cache()
            content_type = content_value or "article"
            pages = int(size_value) if size_value is not None else 3
            return generator.generate_document(content_type, pages, subject_input, file_format)

        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    except Exception as e:
        import pandas as pd
        return None, f"Error generating file: {e}", pd.DataFrame()