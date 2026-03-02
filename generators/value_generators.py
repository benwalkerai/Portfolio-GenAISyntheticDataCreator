"""Value generation functions for individual data fields.

This module contains functions for generating single values like dates,
names, emails, phones, salaries, and statistical distributions.
"""

from __future__ import annotations

import random
import re
from datetime import datetime, timedelta
from typing import Any, Optional

import numpy as np

from .constants import (
    DOMAINS,
    INDUSTRY_KEYWORDS,
    INTERNATIONAL_NAMES,
    LOCATIONS,
)


def generate_lognormal_value(mean: float, stddev: float, 
                            min_val: float, max_val: float) -> float:
    """Generate a lognormal distributed value within bounds.
    
    Args:
        mean: Mean value
        stddev: Standard deviation
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Value from lognormal distribution
    """
    if mean <= 0:
        return random.uniform(min_val, max_val)
    mu = np.log(mean / np.sqrt(1 + (stddev/mean)**2))
    sigma = np.sqrt(np.log(1 + (stddev/mean)**2))
    value = np.random.lognormal(mu, sigma)
    return float(np.clip(value, min_val, max_val))


def generate_normal_value(mean: float, stddev: float, 
                         min_val: float, max_val: float) -> float:
    """Generate a normal distributed value within bounds.
    
    Args:
        mean: Mean value
        stddev: Standard deviation
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Value from normal distribution
    """
    value = np.random.normal(mean, stddev)
    return float(np.clip(value, min_val, max_val))


def generate_power_law_value(alpha: float, min_val: int, max_val: int) -> int:
    """Generate a power law distributed value.
    
    Args:
        alpha: Power law exponent
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Integer from power law distribution
    """
    u = np.random.uniform(0, 1)
    value = min_val * (1 - u) ** (-1 / (alpha - 1))
    return int(np.clip(value, min_val, max_val))


def generate_seasonal_multiplier(date: datetime, pattern: str = 'Q4_peak') -> float:
    """Generate seasonal multiplier based on date and pattern.
    
    Args:
        date: Date to check
        pattern: Seasonal pattern name
        
    Returns:
        Multiplier value
    """
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


def generate_date(start: Optional[datetime] = None,
                 end: Optional[datetime] = None,
                 date_format: str = "%Y-%m-%d",
                 prevent_future: Optional[bool] = None,
                 active_options: Optional[dict] = None) -> str:
    """Generate a random date within specified bounds.
    
    Args:
        start: Start date
        end: End date
        date_format: Output format string
        prevent_future: Whether to prevent future dates
        active_options: Active generation options dict
        
    Returns:
        Formatted date string
    """
    def _coerce_date(value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None
    
    options = active_options or {}
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


def generate_person_name(country: Optional[str] = None) -> str:
    """Generate a realistic person name.
    
    Args:
        country: Optional country for regional name selection
        
    Returns:
        Full name string
    """
    region_map = {
        'USA': 'Anglo', 'UK': 'Anglo', 'Canada': 'Anglo', 'Australia': 'Anglo',
        'Mexico': 'Hispanic', 'Spain': 'Hispanic',
        'China': 'East Asian', 'Japan': 'East Asian', 'Korea': 'East Asian',
        'India': 'South Asian',
        'Germany': 'European', 'France': 'European', 'Italy': 'European'
    }
    region = region_map.get(country or 'USA', 'Anglo')
    name_set = INTERNATIONAL_NAMES.get(region, INTERNATIONAL_NAMES['Anglo'])
    return f"{random.choice(name_set['first'])} {random.choice(name_set['last'])}"


def generate_company_name(subject: Optional[str] = None) -> str:
    """Generate a realistic company name.
    
    Args:
        subject: Optional subject for industry-specific naming
        
    Returns:
        Company name string
    """
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
    keywords = INDUSTRY_KEYWORDS[industry]
    bases = ['Apex', 'Summit', 'Pinnacle', 'Starlight', 'Meridian', 'Global', 
            'Quantum', 'Premier', 'United', 'Pacific']
    style = random.random()
    if style < 0.4:
        return f"{random.choice(bases)} {random.choice(keywords)}"
    elif style < 0.7:
        last = random.choice(INTERNATIONAL_NAMES['Anglo']['last'])
        return f"{last} {random.choice(keywords)}"
    else:
        return f"{random.choice(bases)} {random.choice(INTERNATIONAL_NAMES['Anglo']['last'])} Inc."


def generate_job_title(dept: str) -> str:
    """Generate a job title for a department.
    
    Args:
        dept: Department name
        
    Returns:
        Job title string
    """
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


def generate_phone(country: str = "USA") -> str:
    """Generate a phone number in country-specific format.
    
    Args:
        country: Country code
        
    Returns:
        Formatted phone number
    """
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
    fmt = LOCATIONS.get(country_normalized, {}).get("phone_format", "US")
    return formats.get(fmt, formats["US"])()


def generate_salary(job_title: str, country: str = "USA", 
                   department: Optional[str] = None, 
                   years_experience: Optional[int] = None) -> float:
    """Generate a realistic salary based on job parameters.
    
    Args:
        job_title: Job title
        country: Country location
        department: Optional department
        years_experience: Optional years of experience
        
    Returns:
        Annual salary amount
    """
    base_ranges = {
        "USA": (35000, 150000), "UK": (28000, 120000),
        "Germany": (32000, 130000), "Canada": (33000, 125000),
        "Australia": (40000, 140000), "Japan": (30000, 110000),
        "India": (8000, 50000), "China": (12000, 60000), "France": (30000, 125000)
    }
    low, high = base_ranges.get(country, (30000, 120000))
    mult = LOCATIONS.get(country, {}).get('salary_multiplier', 1.0)
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
    salary = generate_lognormal_value(mean, stddev, low, high * h_mult * exp_mult)
    return round(salary / 100) * 100


def generate_email(first_name: str, last_name: str, 
                  company: Optional[str] = None) -> str:
    """Generate an email address.
    
    Args:
        first_name: First name
        last_name: Last name
        company: Optional company name for domain
        
    Returns:
        Email address string
    """
    first = re.sub(r'[^a-zA-Z]', '', first_name.lower())
    last = re.sub(r'[^a-zA-Z]', '', last_name.lower())
    domain = company or random.choice(DOMAINS)
    if company and ' ' in company:
        domain = company.split()[0].lower() + '.com'
    formats = [
        f"{first}.{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}.{last}{random.randint(1,99)}@{domain}"
    ]
    return random.choice(formats)


def generate_id_with_encoding(prefix: str, index: int) -> str:
    """Generate an ID with prefix and numeric encoding.
    
    Args:
        prefix: ID prefix
        index: Numeric index
        
    Returns:
        Formatted ID string
    """
    idx = int(index) if isinstance(index, (int, float)) else 0
    return f"{prefix}-{idx:05d}"
