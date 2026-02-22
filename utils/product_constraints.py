"""Constraints and validation rules for product catalogs."""

from typing import Dict, List, Tuple, Any, Optional, Callable
import random


class ProductConstraints:
    """Define and validate category-specific product constraints."""
    
    # Category-specific constraints based on real-world product specifications
    CONSTRAINTS: Dict[str, Dict[str, Any]] = {
        "Smartphone": {
            "weight_grams": (140, 250),
            "dimensions_pattern": lambda: f'{random.uniform(5.5, 7.0):.1f}" x {random.uniform(2.5, 3.5):.1f}" x {random.uniform(0.25, 0.35):.2f}"',
            "processor_types": [
                "Qualcomm Snapdragon 8 Gen 2",
                "Qualcomm Snapdragon 8 Gen 1",
                "Apple A16 Bionic",
                "Apple A15 Bionic",
                "MediaTek Dimensity 9200",
                "Google Tensor G2",
                "Samsung Exynos 2200"
            ],
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
            "processor_types": [
                "Intel Core i7-13700H",
                "Intel Core i5-13500H",
                "Intel Core i9-13900HX",
                "AMD Ryzen 7 7840HS",
                "AMD Ryzen 9 7940HS",
                "Apple M2 Pro",
                "Apple M3"
            ],
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
            "processor_types": [
                "Apple A14 Bionic",
                "Qualcomm Snapdragon 8cx Gen 3",
                "MediaTek Kompanio 1300T",
                "Apple M1",
                "Apple M2"
            ],
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
            "processor_types": [
                "Apple S8",
                "Apple S9",
                "Qualcomm Snapdragon W5+ Gen 1",
                "Samsung Exynos W920",
                "Google Wear 4100+"
            ],
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
            "processor_types": [
                "Active Noise Cancellation Chip",
                "Bluetooth 5.3 SoC",
                "Apple H2 Chip",
                "Qualcomm QCC5141",
                "Sony LDAC Processor"
            ],
            "ram_gb": None,  # Not applicable
            "storage_gb": None,  # Not applicable
            "battery_life_hours": (20, 50),
            "screen_size_inches": None,  # Not applicable
            "price_range": (49, 549),
            "valid_subcategories": ["Over-Ear", "On-Ear", "In-Ear", "Gaming", "Studio"],
            "model_prefixes": ["HP-", "WH-", "AP-"]
        },
        "Monitor": {
            "weight_grams": (3000, 8000),
            "dimensions_pattern": lambda: f'{random.uniform(20.0, 35.0):.1f}" x {random.uniform(12.0, 20.0):.1f}" x {random.uniform(1.5, 3.0):.1f}"',
            "processor_types": None,  # Not applicable
            "ram_gb": None,
            "storage_gb": None,
            "battery_life_hours": None,  # Not applicable (AC powered)
            "screen_size_inches": (21.5, 49.0),
            "price_range": (149, 2999),
            "valid_subcategories": ["Gaming", "Professional", "Ultrawide", "4K", "Curved"],
            "model_prefixes": ["MN-", "GM-", "UM-"]
        }
    }
    
    @classmethod
    def get_constraint(cls, category: str, field: str) -> Any:
        """
        Get constraint specification for a specific category and field.
        
        This method retrieves the constraint definition for a given product category
        and field, returning the specification that can be used for validation or
        value generation.
        
        Args:
            category (str): Product category (e.g., "Smartphone", "Laptop")
            field (str): Field name (e.g., "weight_grams", "price_range", "processor_types")
        
        Returns:
            Any: Constraint specification which can be:
                - Tuple: (min_value, max_value) for numeric ranges
                - List: Valid discrete values
                - Callable: Function to generate values
                - None: Field not applicable for this category
        
        Example:
            >>> ProductConstraints.get_constraint("Smartphone", "price_range")
            (299, 1599)
            >>> ProductConstraints.get_constraint("Laptop", "processor_types")
            ['Intel Core i7-13700H', 'Intel Core i5-13500H', ...]
        """
        category_constraints = cls.CONSTRAINTS.get(category, {})
        return category_constraints.get(field)
    
    @classmethod
    def validate_and_fix_row(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fix a single product row based on category constraints.
        
        This method performs comprehensive validation and correction of product data
        based on the category-specific constraints. It ensures that all values
        fall within realistic ranges and follow proper patterns for the product type.
        
        Validation includes:
        - Weight ranges based on product category
        - Dimension pattern generation
        - Processor type validation
        - RAM and storage validation
        - Battery life ranges
        - Screen size validation
        - Subcategory validation
        - Model number generation
        - Price range validation
        
        Args:
            row (Dict[str, Any]): Product data row to validate and fix
        
        Returns:
            Dict[str, Any]: Corrected product data row with realistic values
        
        Example:
            >>> row = {
            ...     "category": "Smartphone",
            ...     "weight_grams": 50,  # Too light
            ...     "price": 50,  # Too cheap
            ...     "processor": "Invalid Processor"
            ... }
            >>> fixed = ProductConstraints.validate_and_fix_row(row)
            >>> print(fixed["weight_grams"])  # Corrected to realistic range
            >>> print(fixed["price"])  # Corrected to realistic price
        """
        category = row.get('category', '')
        
        # If category not in constraints, return as-is
        if category not in cls.CONSTRAINTS:
            return row
        
        constraints = cls.CONSTRAINTS[category]
        fixed_row = row.copy()
        
        # Fix weight
        if 'weight_grams' in row and constraints.get('weight_grams'):
            min_w, max_w = constraints['weight_grams']
            current = row['weight_grams']
            if not isinstance(current, (int, float)) or current < min_w or current > max_w:
                fixed_row['weight_grams'] = random.randint(min_w, max_w)
        
        # Fix dimensions
        if 'dimensions' in row and constraints.get('dimensions_pattern'):
            fixed_row['dimensions'] = constraints['dimensions_pattern']()
        
        # Fix processor
        if 'processor' in row and constraints.get('processor_types'):
            current_processor = str(row.get('processor', ''))
            valid_processors = constraints['processor_types']
            # Check if current processor is in valid list
            if not any(proc in current_processor for proc in valid_processors):
                fixed_row['processor'] = random.choice(valid_processors)
        
        # Fix RAM
        if 'ram_gb' in row and constraints.get('ram_gb'):
            valid_ram = constraints['ram_gb']
            current = row.get('ram_gb')
            if not isinstance(current, (int, float)) or current not in valid_ram:
                fixed_row['ram_gb'] = random.choice(valid_ram)
        
        # Fix Storage
        if 'storage_gb' in row and constraints.get('storage_gb'):
            valid_storage = constraints['storage_gb']
            current = row.get('storage_gb')
            if not isinstance(current, (int, float)) or current not in valid_storage:
                fixed_row['storage_gb'] = random.choice(valid_storage)
        
        # Fix battery life
        if 'battery_life_hours' in row and constraints.get('battery_life_hours'):
            min_b, max_b = constraints['battery_life_hours']
            current = row.get('battery_life_hours')
            if not isinstance(current, (int, float)) or current < min_b or current > max_b:
                fixed_row['battery_life_hours'] = random.randint(int(min_b), int(max_b))
        
        # Fix screen size
        if 'screen_size_inches' in row and constraints.get('screen_size_inches'):
            min_s, max_s = constraints['screen_size_inches']
            current = row.get('screen_size_inches')
            if not isinstance(current, (int, float)) or current < min_s or current > max_s:
                fixed_row['screen_size_inches'] = round(random.uniform(min_s, max_s), 1)
        
        # Fix subcategory
        if 'subcategory' in row and constraints.get('valid_subcategories'):
            valid_subs = constraints['valid_subcategories']
            current = row.get('subcategory', '')
            if current not in valid_subs:
                fixed_row['subcategory'] = random.choice(valid_subs)
        
        # Fix model number - ensure it's unique per product
        if 'model_number' in row and 'product_name' in row and constraints.get('model_prefixes'):
            product_name = row['product_name']
            prefix = random.choice(constraints['model_prefixes'])
            # Generate model from product name
            name_parts = product_name.replace(' ', '').upper()[:6]
            model_suffix = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
            fixed_row['model_number'] = f"{prefix}{name_parts}-{model_suffix}"
        
        # Fix price range
        if 'price' in row and constraints.get('price_range'):
            min_p, max_p = constraints['price_range']
            current = row.get('price')
            # Parse price if it's a string
            if isinstance(current, str):
                current = float(current.replace('$', '').replace(',', ''))
            if not isinstance(current, (int, float)) or current < min_p or current > max_p:
                fixed_row['price'] = round(random.uniform(min_p, max_p), 2)
        
        return fixed_row
    
    @classmethod
    def get_realistic_value(cls, category: str, field: str) -> Any:
        """
        Generate a realistic value for a given category and field.
        
        This method generates a realistic value based on the constraint specification
        for a given product category and field. It handles different types of
        constraints including numeric ranges, discrete choices, and pattern generators.
        
        Args:
            category (str): Product category (e.g., "Smartphone", "Laptop")
            field (str): Field name (e.g., "weight_grams", "processor_types")
        
        Returns:
            Any: Generated realistic value, or None if field not applicable
        
        Example:
            >>> ProductConstraints.get_realistic_value("Smartphone", "weight_grams")
            185  # Random integer between 140-250
            >>> ProductConstraints.get_realistic_value("Laptop", "processor_types")
            "Intel Core i7-13700H"  # Random choice from valid processors
        """
        constraints = cls.CONSTRAINTS.get(category, {})
        
        if field not in constraints or constraints[field] is None:
            return None
        
        value_spec = constraints[field]
        
        # Handle tuple ranges (min, max)
        if isinstance(value_spec, tuple) and len(value_spec) == 2:
            min_val, max_val = value_spec
            if isinstance(min_val, int) and isinstance(max_val, int):
                return random.randint(min_val, max_val)
            else:
                return round(random.uniform(min_val, max_val), 2)
        
        # Handle lists (discrete choices)
        elif isinstance(value_spec, list):
            return random.choice(value_spec)
        
        # Handle callables (like dimensions_pattern)
        elif callable(value_spec):
            return value_spec()
        
        return None
    
    @classmethod
    def get_validation_rules(cls, category: str) -> Dict[str, str]:
        """
        Get human-readable validation rules for a product category.
        
        This method provides a human-readable summary of all validation rules
        and constraints for a given product category. It's useful for debugging,
        documentation, and understanding what constraints are applied.
        
        Args:
            category (str): Product category to get rules for
        
        Returns:
            Dict[str, str]: Dictionary mapping field names to human-readable rule descriptions
        
        Example:
            >>> rules = ProductConstraints.get_validation_rules("Smartphone")
            >>> print(rules["weight_grams"])
            "Range: 140 to 250"
            >>> print(rules["processor_types"])
            "Valid values: Qualcomm Snapdragon 8 Gen 2, Qualcomm Snapdragon 8 Gen 1, Apple A16 Bionic..."
        """
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


# Validation function for use in data generation pipeline
def apply_product_constraints(df: Any) -> Any:
    """
    Apply product constraints to an entire DataFrame.
    
    This function processes an entire DataFrame by applying product constraints
    to each row individually. It's designed to be used in data generation
    pipelines to ensure all generated product data follows realistic constraints.
    
    Args:
        df: Pandas DataFrame containing product data to validate and fix
    
    Returns:
        pandas.DataFrame: DataFrame with all rows corrected according to constraints
    
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame([
        ...     {"category": "Smartphone", "weight_grams": 50, "price": 50},
        ...     {"category": "Laptop", "weight_grams": 500, "price": 200}
        ... ])
        >>> fixed_df = apply_product_constraints(df)
        >>> print(fixed_df["weight_grams"])  # All weights corrected to realistic ranges
    """
    import pandas as pd
    
    fixed_rows = []
    for idx, row in df.iterrows():
        fixed_row = ProductConstraints.validate_and_fix_row(row.to_dict())
        fixed_rows.append(fixed_row)
    
    return pd.DataFrame(fixed_rows)
