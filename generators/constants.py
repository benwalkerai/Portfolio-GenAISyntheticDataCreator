"""Static constants and reference data for data generation.

This module contains all static reference data including product catalogs,
location data, industry keywords, and other constants used across generators.
"""

from __future__ import annotations


PRODUCT_NAMES = {
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

LOCATIONS = {
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
    },
    'France': {
        'states': ['Île-de-France', 'Provence', 'Rhône-Alpes', 'Brittany'],
        'cities': ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg'],
        'currency': 'EUR',
        'currency_symbol': '€',
        'salary_multiplier': 0.92,
        'phone_format': 'FR',
        'decimal_separator': ','
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

INTERNATIONAL_NAMES = {
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

INDUSTRY_KEYWORDS = {
    'generic': ['Solutions', 'Systems', 'Services', 'Works'],
    'tech': ['Technologies', 'Labs', 'Systems', 'Soft'],
    'finance': ['Capital', 'Investments', 'Holdings'],
    'manufacturing': ['Manufacturing', 'Industries', 'Supply'],
    'healthcare': ['Health', 'Medical', 'Care']
}

DOMAINS = ['example.com', 'company.com', 'corporate.com']

STREET_NAMES = ['Maple', 'Oak', 'Pine', 'Cedar', 'Elm', 'Washington', 'Main', 'Park', 
                'Sunset', 'River', 'Lake', 'Hill', 'Valley', 'Forest', 'Meadow', 'Spring',
                'Grove', 'Ridge', 'Bay', 'Shore']

STREET_TYPES = ['St', 'Ave', 'Blvd', 'Rd', 'Ln', 'Dr', 'Ct', 'Way', 'Pl', 'Ter', 'Cir']

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

# Financial Transaction Merchant-Category Mappings
# Each category maps to appropriate merchants and transaction characteristics
FINANCIAL_MERCHANTS = {
    'Housing': {
        'merchants': [
            'ABC Mortgage Company', 'First National Mortgage', 'Home Loans Inc',
            'Apartment Management Co', 'Property Rentals LLC', 'City Housing Authority',
            'Metropolitan Property Management', 'Riverside Apartments'
        ],
        'transaction_types': ['Payment', 'ACH'],
        'recurring': True,  # These are typically recurring monthly payments
        'amount_range': (800, 3500)
    },
    'Utilities': {
        'merchants': [
            'Electric Company', 'Power & Light', 'City Electric Utility',
            'Water Utility', 'City Water & Sewer', 'Municipal Water District',
            'Natural Gas Company', 'Gas & Electric', 'Waste Management Services',
            'Internet Services Inc', 'Comcast', 'AT&T', 'Verizon Wireless',
            'T-Mobile', 'Spectrum Internet'
        ],
        'transaction_types': ['Payment', 'ACH'],
        'recurring': True,
        'amount_range': (45, 250)
    },
    'Groceries': {
        'merchants': [
            'Whole Foods Market', "Trader Joe's", 'Safeway', 'Kroger', 'Publix',
            'Target Grocery', 'Walmart Supercenter', 'Costco Wholesale', 'Aldi',
            "Sam's Club", 'Fresh Market', 'Sprouts Farmers Market'
        ],
        'transaction_types': ['Debit', 'Credit'],
        'recurring': False,
        'amount_range': (30, 250)
    },
    'Restaurants': {
        'merchants': [
            'Starbucks', "McDonald's", 'Chipotle Mexican Grill', 'Panera Bread',
            'Subway', 'Olive Garden', 'Chick-fil-A', "Domino's Pizza", 'Taco Bell',
            'Five Guys', "Wendy's", 'In-N-Out Burger', 'The Cheesecake Factory',
            'Local Bistro', 'Downtown Cafe'
        ],
        'transaction_types': ['Debit', 'Credit'],
        'recurring': False,
        'amount_range': (8, 85)
    },
    'Transportation': {
        'merchants': [
            'Shell Gas Station', 'Chevron', 'Exxon', 'BP', '7-Eleven Fuel',
            'Uber', 'Lyft', 'City Transit Authority', 'Metro Rail Pass',
            'Parking Garage Downtown', 'Airport Parking'
        ],
        'transaction_types': ['Debit', 'Credit'],
        'recurring': False,
        'amount_range': (5, 120)
    },
    'Shopping': {
        'merchants': [
            'Amazon.com', 'Target', 'Walmart', 'Best Buy', 'Home Depot', "Lowe's",
            "Macy's", 'Nordstrom', "Kohl's", 'TJ Maxx', 'Old Navy', 'Nike Store',
            'Apple Store', 'REI', 'IKEA'
        ],
        'transaction_types': ['Debit', 'Credit'],
        'recurring': False,
        'amount_range': (15, 500)
    },
    'Healthcare': {
        'merchants': [
            'CVS Pharmacy', 'Walgreens', 'Rite Aid', 'City Medical Center',
            'Dental Care Associates', 'Vision Center', 'HealthCare Insurance Co',
            'Medical Group Practice', 'Urgent Care Clinic'
        ],
        'transaction_types': ['Payment', 'Debit', 'Credit'],
        'recurring': False,
        'amount_range': (25, 450)
    },
    'Entertainment': {
        'merchants': [
            'Netflix', 'Spotify', 'Disney+', 'Hulu', 'HBO Max', 'Apple iTunes',
            'Google Play', 'Amazon Prime Video', 'AMC Theaters', 'Regal Cinemas',
            'Live Nation', 'Ticketmaster', 'PlayStation Network', 'Xbox Live'
        ],
        'transaction_types': ['Credit'],
        'recurring': True,  # Many entertainment subscriptions are recurring
        'amount_range': (9.99, 120)
    },
    'Travel': {
        'merchants': [
            'Delta Airlines', 'United Airlines', 'American Airlines', 'Southwest Airlines',
            'Marriott Hotels', 'Hilton Hotels', 'Hyatt Hotels', 'Airbnb',
            'Expedia', 'Booking.com', 'Hertz Rent-A-Car', 'Enterprise Car Rental'
        ],
        'transaction_types': ['Credit'],
        'recurring': False,
        'amount_range': (150, 1500)
    },
    'Insurance': {
        'merchants': [
            'State Farm Insurance', 'Geico', 'Progressive Insurance', 'Allstate',
            'Liberty Mutual', 'Health Insurance Co', 'Life Insurance Group'
        ],
        'transaction_types': ['Payment', 'ACH'],
        'recurring': True,
        'amount_range': (120, 650)
    },
    'Income': {
        'merchants': [
            'Employer Direct Deposit', 'Payroll Services Inc', 'Salary Payment',
            'Freelance Client Payment', 'Contract Work Payment', 'Bonus Payment',
            'Investment Dividend', 'Interest Payment'
        ],
        'transaction_types': ['Deposit', 'Transfer'],
        'recurring': True,
        'amount_range': (1500, 8000)
    },
    'Transfers': {
        'merchants': [
            'Bank Transfer', 'Internal Transfer', 'Savings Transfer',
            'Investment Account Transfer', 'Zelle Transfer', 'Venmo',
            'PayPal', 'Cash App'
        ],
        'transaction_types': ['Transfer'],
        'recurring': False,
        'amount_range': (50, 2000)
    }
}
