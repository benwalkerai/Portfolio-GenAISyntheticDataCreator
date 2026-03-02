"""Employee data generation functions.

This module provides specialized generation for employee datasets
including hierarchies, departments, and realistic distributions.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Set

import pandas as pd

from .constants import LOCATIONS
from .llm_utils import extract_json, generate_with_llm
from .value_generators import (
    generate_email,
    generate_phone,
    generate_id_with_encoding,
    generate_salary,
)


def generate_employee_data(data_generator: Any, llm_cache: Dict[str, str],
                          rows: int, columns: int, subject: str) -> pd.DataFrame:
    """Generate realistic employee data with hierarchy.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        rows: Number of employee records
        columns: Number of columns (unused, uses predefined schema)
        subject: Subject context
        
    Returns:
        DataFrame with employee data
    """
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
        batch_data = _generate_employee_batch_with_llm(
            data_generator, llm_cache, current_batch,
            used_first_names, used_last_names
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
        new_batch = _generate_employee_batch_with_llm(
            data_generator, llm_cache, 1, used_first_names, used_last_names
        )
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
    df['EmployeeID'] = [generate_id_with_encoding('EMP', i) for i in range(rows)]
    countries = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France']
    df['Country'] = [random.choice(countries) for _ in range(rows)]
    df['City'] = df['Country'].apply(lambda c: random.choice(LOCATIONS.get(c, LOCATIONS['USA'])['cities']))
    df['Email'] = df.apply(lambda x: generate_email(x['FirstName'], x['LastName']), axis=1)
    df['PhoneNumber'] = df['Country'].apply(lambda c: generate_phone(c))
    now = datetime.now()
    df['HireDate'] = [(now - timedelta(days=random.randint(30, 365*10))).strftime('%Y-%m-%d') for _ in range(rows)]
    df['Status'] = random.choices(['Active', 'On Leave', 'Terminated'], weights=[0.9, 0.05, 0.05], k=rows)
    df['Salary'] = df.apply(lambda x: generate_salary(x['JobTitle'], x['Country'], x['Department']), axis=1)
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


def _generate_employee_batch_with_llm(data_generator: Any, llm_cache: Dict[str, str],
                                     count: int, 
                                     used_first_names: Set[str],
                                     used_last_names: Set[str]) -> List[Dict]:
    """Generate a batch of employee profiles using LLM.
    
    Args:
        data_generator: Data generator instance
        llm_cache: LLM cache dictionary
        count: Number of employees to generate
        used_first_names: Set of already used first names
        used_last_names: Set of already used last names
        
    Returns:
        List of employee dictionaries
    """
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
        response = generate_with_llm(data_generator, llm_cache, prompt, max_tokens=2000)
        cleaned_json = extract_json(response)
        if cleaned_json:
            data = json.loads(cleaned_json)
            if isinstance(data, list):
                return data
    except Exception as e:
        print(f"   LLM batch generation failed: {e}")
    return []
