"""Schema templates and fallback schemas for data generation.

This module provides template-based schemas for common data types when
LLM generation is not available or fails.
"""

from __future__ import annotations

from typing import Dict, List

from .constants import LOCATIONS, PRODUCT_NAMES


def create_enhanced_fallback_schema(subject: str, num_columns: int) -> List[Dict]:
    """Create a template-based schema when LLM generation fails.
    
    Args:
        subject: Subject/domain for the schema
        num_columns: Number of columns needed
        
    Returns:
        List of column schema dictionaries
    """
    print(f" Creating fallback schema for '{subject}'")
    base_schemas = {
        'employee': [
            {"name": "EmployeeID", "type": "id", "examples": ["EMP-10234"], "description": "Unique employee identifier"},
            {"name": "FirstName", "type": "text", "examples": ["John", "Maria"], "description": "Employee first name"},
            {"name": "LastName", "type": "text", "examples": ["Smith", "Garcia"], "description": "Employee last name"},
            {"name": "Email", "type": "email", "examples": ["john.smith@company.com"], "description": "Work email"},
            {"name": "Department", "type": "category", "examples": ["IT", "Finance", "HR", "Marketing"], "description": "Department"},
            {"name": "JobTitle", "type": "text", "examples": ["Software Engineer", "Manager"], "description": "Job position"},
            {"name": "Manager", "type": "text", "examples": ["Jane Doe"], "description": "Reports to"},
            {"name": "HireDate", "type": "date", "examples": ["2020-03-15"], "description": "Date hired"},
            {"name": "Salary", "type": "money", "examples": ["65000"], "description": "Annual salary"},
            {"name": "PhoneNumber", "type": "phone", "examples": ["555-123-4567"], "description": "Contact phone"},
            {"name": "Country", "type": "category", "examples": list(LOCATIONS.keys()), "description": "Work location"},
            {"name": "City", "type": "text", "examples": ["New York"], "description": "City"},
            {"name": "Status", "type": "category", "examples": ["Active", "On Leave"], "description": "Employment status"}
        ],
        'sales': [
            {"name": "OrderID", "type": "id", "examples": ["ORD-50123"], "description": "Order number"},
            {"name": "OrderDate", "type": "date", "examples": ["2025-01-15"], "description": "Date ordered"},
            {"name": "CustomerID", "type": "id", "examples": ["CUST-1234"], "description": "Customer ID"},
            {"name": "CustomerName", "type": "text", "examples": ["Acme Corp"], "description": "Customer"},
            {"name": "ProductSKU", "type": "id", "examples": ["ELEC-QU4K-1234"], "description": "Product SKU"},
            {"name": "ProductName", "type": "text", "examples": ["Quantum 4K Display"], "description": "Product"},
            {"name": "Category", "type": "category", "examples": list(PRODUCT_NAMES.keys()), "description": "Product category"},
            {"name": "Quantity", "type": "number", "examples": ["1", "5"], "description": "Quantity sold"},
            {"name": "UnitPrice", "type": "money", "examples": ["99.99"], "description": "Price per unit"},
            {"name": "TotalSale", "type": "money", "examples": ["499.95"], "description": "Total amount"},
            {"name": "SalesRep", "type": "text", "examples": ["John Smith"], "description": "Sales representative"},
            {"name": "Region", "type": "category", "examples": ["North", "South", "East", "West"], "description": "Sales region"},
            {"name": "Status", "type": "category", "examples": ["Completed", "Pending"], "description": "Order status"}
        ],
        'product': [
            {"name": "ProductID", "type": "id", "examples": ["PROD-1001"], "description": "Product ID"},
            {"name": "ProductName", "type": "text", "examples": ["Quantum 4K Display"], "description": "Product name"},
            {"name": "SKU", "type": "id", "examples": ["ELEC-QU4K-1234"], "description": "Stock keeping unit"},
            {"name": "Category", "type": "category", "examples": list(PRODUCT_NAMES.keys()), "description": "Category"},
            {"name": "Price", "type": "money", "examples": ["299.99"], "description": "Retail price"},
            {"name": "Cost", "type": "money", "examples": ["150.00"], "description": "Cost basis"},
            {"name": "StockQuantity", "type": "number", "examples": ["50"], "description": "Current stock"},
            {"name": "ReorderLevel", "type": "number", "examples": ["10"], "description": "Reorder threshold"},
            {"name": "Supplier", "type": "text", "examples": ["Global Manufacturing"], "description": "Supplier name"},
            {"name": "DateAdded", "type": "date", "examples": ["2023-06-15"], "description": "Added to catalog"}
        ],
        'customer': [
            {"name": "CustomerID", "type": "id", "examples": ["CUST-5001"], "description": "Unique customer identifier"},
            {"name": "CompanyName", "type": "text", "examples": ["Acme Corporation", "Global Industries"], "description": "Company name"},
            {"name": "Industry", "type": "category", "examples": ["Technology", "Manufacturing", "Retail", "Healthcare", "Finance"], "description": "Industry sector"},
            {"name": "ContactPerson", "type": "text", "examples": ["John Smith", "Maria Garcia"], "description": "Primary contact"},
            {"name": "Email", "type": "email", "examples": ["contact@acme.com"], "description": "Contact email"},
            {"name": "PhoneNumber", "type": "phone", "examples": ["555-123-4567"], "description": "Contact phone"},
            {"name": "Country", "type": "category", "examples": list(LOCATIONS.keys()), "description": "Country"},
            {"name": "City", "type": "text", "examples": ["New York"], "description": "City"},
            {"name": "AccountStatus", "type": "category", "examples": ["Active", "Inactive", "Pending"], "description": "Account status"},
            {"name": "CreditLimit", "type": "money", "examples": ["50000"], "description": "Credit limit"},
            {"name": "JoinDate", "type": "date", "examples": ["2020-03-15"], "description": "Customer since"},
            {"name": "LastOrderDate", "type": "date", "examples": ["2024-12-01"], "description": "Last order date"}
        ],
        'supplier': [
            {"name": "SupplierID", "type": "id", "examples": ["SUP-3001"], "description": "Unique supplier identifier"},
            {"name": "CompanyName", "type": "text", "examples": ["Global Manufacturing", "Tech Supplies Inc"], "description": "Supplier company name"},
            {"name": "Industry", "type": "category", "examples": ["Manufacturing", "Distribution", "Technology", "Raw Materials"], "description": "Industry sector"},
            {"name": "ContactPerson", "type": "text", "examples": ["Jane Doe", "Carlos Martinez"], "description": "Primary contact"},
            {"name": "Email", "type": "email", "examples": ["sales@supplier.com"], "description": "Contact email"},
            {"name": "PhoneNumber", "type": "phone", "examples": ["555-987-6543"], "description": "Contact phone"},
            {"name": "PaymentTerms", "type": "category", "examples": ["Net 30", "Net 60", "Net 90", "COD", "Prepaid"], "description": "Payment terms"},
            {"name": "MinimumOrder", "type": "money", "examples": ["1000", "5000"], "description": "Minimum order amount"},
            {"name": "LeadTime", "type": "number", "examples": ["7", "14", "30"], "description": "Lead time in days"},
            {"name": "Country", "type": "category", "examples": list(LOCATIONS.keys()), "description": "Country"},
            {"name": "City", "type": "text", "examples": ["Shanghai"], "description": "City"},
            {"name": "Status", "type": "category", "examples": ["Active", "Inactive", "Pending"], "description": "Supplier status"}
        ],
        'support': [
            {"name": "TicketID", "type": "id", "examples": ["TKT-10234"], "description": "Ticket number"},
            {"name": "DateCreated", "type": "date", "examples": ["2025-08-15"], "description": "Created date"},
            {"name": "CustomerName", "type": "text", "examples": ["John Smith"], "description": "Customer"},
            {"name": "Email", "type": "email", "examples": ["john@example.com"], "description": "Contact email"},
            {"name": "Priority", "type": "category", "examples": ["Low", "Medium", "High", "Critical"], "description": "Priority level"},
            {"name": "Status", "type": "category", "examples": ["Open", "In Progress", "Resolved"], "description": "Ticket status"},
            {"name": "AssignedTo", "type": "text", "examples": ["Support Agent 1"], "description": "Assigned agent"},
            {"name": "Category", "type": "category", "examples": ["Technical", "Billing", "General"], "description": "Issue category"},
            {"name": "Subject", "type": "text", "examples": ["Login issue"], "description": "Issue summary"},
            {"name": "Resolution", "type": "text", "examples": ["Password reset sent"], "description": "Resolution details"}
        ],
        'financial': [
            {"name": "TransactionID", "type": "id", "examples": ["TXN-89234567"], "description": "Unique transaction identifier"},
            {"name": "AccountNumber", "type": "id", "examples": ["ACC-123456789"], "description": "Account number"},
            {"name": "TransactionDate", "type": "date", "examples": ["2025-01-15"], "description": "Transaction date"},
            {"name": "PostedDate", "type": "date", "examples": ["2025-01-16"], "description": "Posted date"},
            {"name": "TransactionType", "type": "category", "examples": ["Debit", "Credit", "Transfer", "Payment", "Deposit", "ACH"], "description": "Transaction type"},
            {"name": "Amount", "type": "money", "examples": ["1234.56"], "description": "Transaction amount"},
            {"name": "Currency", "type": "category", "examples": ["USD", "EUR", "GBP", "JPY", "CAD"], "description": "Currency"},
            {"name": "Balance", "type": "money", "examples": ["45678.90"], "description": "Account balance after transaction"},
            {"name": "MerchantName", "type": "text", "examples": ["Amazon", "Walmart", "Shell Gas Station"], "description": "Merchant or payee"},
            {"name": "Category", "type": "category", "examples": ["Groceries", "Utilities", "Entertainment", "Travel", "Healthcare", "Shopping", "Housing", "Transportation", "Restaurants", "Insurance", "Income", "Transfers"], "description": "Transaction category"},
            {"name": "PaymentMethod", "type": "category", "examples": ["Card", "ACH", "Wire", "Check", "Cash"], "description": "Payment method"},
            {"name": "Status", "type": "category", "examples": ["Posted", "Pending", "Cleared"], "description": "Transaction status"},
            {"name": "Description", "type": "text", "examples": ["Purchase at store", "Monthly payment"], "description": "Transaction description"},
            {"name": "AuthCode", "type": "id", "examples": ["AUTH-ABC123"], "description": "Authorization code"},
            {"name": "Notes", "type": "text", "examples": ["", "Recurring monthly"], "description": "Additional notes"}
        ]
    }
    subject_lower = subject.lower()
    key = 'employee'
    if 'financial' in subject_lower and 'transaction' in subject_lower:
        key = 'financial'
    elif any(s in subject_lower for s in ['customer', 'client', 'account']):
        key = 'customer'
    elif any(s in subject_lower for s in ['supplier', 'vendor', 'provider']):
        key = 'supplier'
    elif any(s in subject_lower for s in ['sale', 'order', 'transaction', 'invoice']):
        key = 'sales'
    elif any(s in subject_lower for s in ['product', 'inventory', 'catalog', 'item']):
        key = 'product'
    elif any(s in subject_lower for s in ['support', 'ticket', 'help', 'issue']):
        key = 'support'
    schema = base_schemas[key].copy()
    if len(schema) < num_columns:
        schema = _pad_schema(schema, num_columns, subject)
    return schema[:num_columns]


def _pad_schema(schema: List[Dict], target: int, subject: str) -> List[Dict]:
    """Pad schema with generic columns if needed.
    
    Args:
        schema: Current schema
        target: Target number of columns
        subject: Subject context
        
    Returns:
        Padded schema
    """
    generic = [
        {"name": "CreatedDate", "type": "date", "examples": ["2024-01-15"], "description": "Record created"},
        {"name": "LastModified", "type": "date", "examples": ["2025-08-10"], "description": "Last updated"},
        {"name": "IsActive", "type": "boolean", "examples": ["True", "False"], "description": "Active status"},
        {"name": "Notes", "type": "text", "examples": ["", "Check details"], "description": "Additional notes"},
        {"name": "Status", "type": "category", "examples": ["Active", "Pending"], "description": "Status"},
        {"name": "Priority", "type": "category", "examples": ["Low", "Medium", "High"], "description": "Priority"},
        {"name": "Tags", "type": "text", "examples": ["tag1,tag2"], "description": "Tags"},
        {"name": "Source", "type": "category", "examples": ["Web", "Mobile", "API"], "description": "Data source"}
    ]
    while len(schema) < target and generic:
        schema.append(generic.pop(0))
    return schema[:target]
