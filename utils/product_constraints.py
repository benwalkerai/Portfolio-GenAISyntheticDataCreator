import random


class ProductConstraints:
    
    CONSTRAINTS = {
        "Smartphone": {
            "weight_grams": (140, 250),
            "dimensions_pattern": lambda: f'{random.uniform(5.5, 7.0):.1f}" x {random.uniform(2.5, 3.5):.1f}" x {random.uniform(0.25, 0.35):.2f}"',
            "processor_types": ["Qualcomm Snapdragon 8 Gen 2", "Qualcomm Snapdragon 8 Gen 1", "Apple A16 Bionic", "Apple A15 Bionic", "MediaTek Dimensity 9200", "Google Tensor G2", "Samsung Exynos 2200"],
            "ram_gb": [4, 6, 8, 12, 16],
            "storage_gb": [64, 128, 256, 512, 1024],
            "battery_life_hours": (8, 20),
            "screen_size_inches": (5.5, 7.0),
            "price_range": (299, 1599),
            "valid_subcategories": ["Flagship", "Mid-Range", "Budget", "Foldable Phone", "Gaming Phone"],
            "model_prefixes": ["SM-", "PH-", "IP-", "MT-", "GG-"]
        },
        "Laptop": {
            "weight_grams": (1200, 2800),
            "dimensions_pattern": lambda: f'{random.uniform(13.0, 17.0):.1f}" x {random.uniform(9.0, 12.0):.1f}" x {random.uniform(0.5, 0.9):.2f}"',
            "processor_types": ["Intel Core i7-13700H", "Intel Core i5-13500H", "Intel Core i9-13900HX", "AMD Ryzen 7 7840HS", "AMD Ryzen 9 7940HS", "Apple M2 Pro", "Apple M3"],
            "ram_gb": [8, 16, 32, 64],
            "storage_gb": [256, 512, 1024, 2048],
            "battery_life_hours": (4, 15),
            "screen_size_inches": (13.0, 17.3),
            "price_range": (599, 3999),
            "valid_subcategories": ["Ultrabook", "Gaming Laptop", "Business Laptop", "2-in-1", "Workstation"],
            "model_prefixes": ["UB-", "GL-", "BL-", "WS-"]
        },
        "Tablet": {
            "weight_grams": (300, 700),
            "dimensions_pattern": lambda: f'{random.uniform(9.0, 13.0):.1f}" x {random.uniform(6.0, 9.0):.1f}" x {random.uniform(0.2, 0.3):.2f}"',
            "processor_types": ["Apple A14 Bionic", "Qualcomm Snapdragon 8cx Gen 3", "MediaTek Kompanio 1300T", "Apple M1", "Apple M2"],
            "ram_gb": [4, 6, 8, 16],
            "storage_gb": [64, 128, 256, 512, 1024],
            "battery_life_hours": (8, 14),
            "screen_size_inches": (8.0, 13.0),
            "price_range": (199, 1899),
            "valid_subcategories": ["Standard", "Pro", "Kids", "E-Reader"],
            "model_prefixes": ["TB-", "IP-", "GT-"]
        },
        "Smartwatch": {
            "weight_grams": (25, 65),
            "dimensions_pattern": lambda: f'{random.uniform(1.5, 2.0):.2f}" x {random.uniform(1.5, 2.0):.2f}" x {random.uniform(0.4, 0.6):.2f}"',
            "processor_types": ["Apple S8", "Apple S9", "Qualcomm Snapdragon W5+ Gen 1", "Samsung Exynos W920", "Google Wear 4100+"],
            "ram_gb": [1, 2],
            "storage_gb": [8, 16, 32, 64],
            "battery_life_hours": (18, 72),
            "screen_size_inches": (1.2, 2.0),
            "price_range": (199, 899),
            "valid_subcategories": ["Fitness", "Luxury", "Sport", "Hybrid"],
            "model_prefixes": ["SW-", "AW-", "GW-"]
        },
        "Headphones": {
            "weight_grams": (150, 350),
            "dimensions_pattern": lambda: f'{random.uniform(6.0, 8.0):.1f}" x {random.uniform(6.0, 8.0):.1f}" x {random.uniform(2.0, 3.5):.1f}"',
            "processor_types": ["Active Noise Cancellation Chip", "Bluetooth 5.3 SoC", "Apple H2 Chip", "Qualcomm QCC5141", "Sony LDAC Processor"],
            "battery_life_hours": (20, 50),
            "price_range": (49, 549),
            "valid_subcategories": ["Over-Ear", "On-Ear", "In-Ear", "Gaming", "Studio"],
            "model_prefixes": ["HP-", "WH-", "AP-"]
        },
        "Monitor": {
            "weight_grams": (3000, 8000),
            "dimensions_pattern": lambda: f'{random.uniform(20.0, 35.0):.1f}" x {random.uniform(12.0, 20.0):.1f}" x {random.uniform(1.5, 3.0):.1f}"',
            "screen_size_inches": (21.5, 49.0),
            "price_range": (149, 2999),
            "valid_subcategories": ["Gaming", "Professional", "Ultrawide", "4K", "Curved"],
            "model_prefixes": ["MN-", "GM-", "UM-"]
        }
    }
    
    @classmethod
    def get_constraint(cls, category, field):
        
        category_constraints = cls.CONSTRAINTS.get(category, {})
        return category_constraints.get(field)
    
    @classmethod
    def validate_and_fix_row(cls, row):
        category = row.get('category', '')
        if category not in cls.CONSTRAINTS:
            return row
        constraints = cls.CONSTRAINTS[category]
        fixed_row = row.copy()
        for field, spec in constraints.items():
            if field not in row or not spec:
                continue
            current = row[field]
            if isinstance(spec, tuple):
                min_v, max_v = spec
                if not isinstance(current, (int, float)) or current < min_v or current > max_v:
                    fixed_row[field] = random.randint(min_v, max_v) if isinstance(min_v, int) else round(random.uniform(min_v, max_v), 2)
            elif isinstance(spec, list):
                if current not in spec:
                    fixed_row[field] = random.choice(spec)
            elif callable(spec):
                fixed_row[field] = spec()
        if 'processor' in row and constraints.get('processor_types'):
            current_processor = str(row.get('processor', ''))
            valid_processors = constraints['processor_types']
            if not any(proc in current_processor for proc in valid_processors):
                fixed_row['processor'] = random.choice(valid_processors)
        if 'subcategory' in row and constraints.get('valid_subcategories'):
            current = row.get('subcategory', '')
            if current not in constraints['valid_subcategories']:
                fixed_row['subcategory'] = random.choice(constraints['valid_subcategories'])
        if 'price' in row and constraints.get('price_range'):
            current = row.get('price')
            if isinstance(current, str):
                current = float(current.replace('$', '').replace(',', ''))
            min_p, max_p = constraints['price_range']
            if not isinstance(current, (int, float)) or current < min_p or current > max_p:
                fixed_row['price'] = round(random.uniform(min_p, max_p), 2)
        if 'model_number' in row and 'product_name' in row and constraints.get('model_prefixes'):
            product_name = row['product_name']
            prefix = random.choice(constraints['model_prefixes'])
            name_parts = product_name.replace(' ', '').upper()[:6]
            model_suffix = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
            fixed_row['model_number'] = f"{prefix}{name_parts}-{model_suffix}"
        return fixed_row
    
    @classmethod
    def get_realistic_value(cls, category, field):
        
        constraints = cls.CONSTRAINTS.get(category, {})
        
        if field not in constraints or constraints[field] is None:
            return None
        
        value_spec = constraints[field]
        
        if isinstance(value_spec, tuple) and len(value_spec) == 2:
            min_val, max_val = value_spec
            if isinstance(min_val, int) and isinstance(max_val, int):
                return random.randint(min_val, max_val)
            else:
                return round(random.uniform(min_val, max_val), 2)
        
        elif isinstance(value_spec, list):
            return random.choice(value_spec)
        
        elif callable(value_spec):
            return value_spec()
        
        return None
    
    @classmethod
    def get_validation_rules(cls, category):
        
        if category not in cls.CONSTRAINTS:
            return {}
        
        constraints = cls.CONSTRAINTS[category]
        rules = {}
        
        for field, spec in constraints.items():
            if spec is None:
                rules[field] = "Not applicable"
            elif isinstance(spec, tuple):
                rules[field] = f"Range: {spec[0]} to {spec[1]}"
            elif isinstance(spec, list):
                rules[field] = f"Valid values: {', '.join(map(str, spec[:3]))}{'...' if len(spec) > 3 else ''}"
            elif callable(spec):
                rules[field] = "Generated pattern"
        
        return rules


def apply_product_constraints(df):
    
    import pandas as pd
    
    fixed_rows = []
    for idx, row in df.iterrows():
        fixed_row = ProductConstraints.validate_and_fix_row(row.to_dict())
        fixed_rows.append(fixed_row)
    
    return pd.DataFrame(fixed_rows)
