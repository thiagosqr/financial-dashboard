import pandas as pd
import numpy as np
import random

# Unique accounts with one-to-one account ID mapping
account_id_mapping = {
    "ANZ": 1001,
    "Business Bank Account #1": 1002,
    "CBA": 1003,
    "Petty Cash/Cash On Hand": 1004,
    "Electronic Clearing Account": 1005,
    "Payroll Clearing Account": 1006,
    "Trade Debtors": 2001,
    "Account receivable": 2002,
    "Inventory": 3001,
    "GST Collected": 4001,
    "GST Paid": 4002,
    "ABN Withholdings Payable": 5001,
    "PAYG Withholding Payable": 5002,
    "Superannuation Fund #5": 5003,
    "Other Payroll Liabilities": 5004,
    "Trade Creditors": 5005,
    "Owner's/Shareholder's Capital": 6001,
    "Accounting/Bookkeeping Fees": 7001,
    "Advertising & Marketing": 7002,
    "Bad Debts": 7003,
    "Cleaning Expenses": 7004,
    "Electricity Expenses": 7005,
    "Gas Expenses": 7006,
    "Legal Fees": 7007,
    "Parking/Tolls Expenses": 7008,
    "General Repairs & Maintenance": 7009,
    "Printing": 7010,
    "Internet": 7011,
    "Computer Expenses": 7012,
    "Council Rates": 7013,
    "Water Expenses": 7014,
    "Stationery": 7015,
    "Waste Removal": 7016,
    "Telephone Expenses": 7017,
    "Postage": 7018,
    "Freight Out": 7019,
    "Late Fees Paid": 7020,
    "Discounts Given": 7021,
    "Wages & Salaries Expenses": 7022,
    "Work Cover Premiums": 7023,
    "Uniforms": 7024,
    "Staff Training Expenses": 7025,
    "Director's Fees": 7026,
    "Travel & Accom. Expenses": 7027,
    "Food": 7028,
    "Mobile Phone Expenses": 7029,
    "Other Payroll Expenses": 7030,
    "Furniture Depreciation": 7031,
    "Office Equipment Depreciation": 7032,
    "Computer Depreciation": 7033,
    "Plant & Equipment": 3002,
    "Motor Vehicle Depreciation": 7034,
    "Low Value Pool Depreciation": 7035,
    "Motor Vehicle": 3003,
    "Office furniture and equipment": 3004,
    "Motor Vehicle Registration": 7036,
    "Motor Vehicle Insurance": 7037,
    "Motor Vehicle Fuel/Oil": 7038,
    "Interest Income": 8001,
    "Other Income": 8002
}

# Get unique accounts from the mapping keys
unique_accounts = list(account_id_mapping.keys())

# Transaction type pools
transaction_types = {
    "bank": ["Receive money", "Spend money", "Transfer money", "General journal"],
    "receivable": ["Invoice", "Invoice payment", "Customer return applied"],
    "payable": ["Bill", "Bill payment", "Spend money"],
    "expense": ["Bill", "Bill payment", "Spend money", "General journal"],
    "income": ["Invoice", "Invoice payment", "Receive money"],
    "equity": ["General journal", "Receive money"],
    "tax": ["Bill payment", "Spend money", "Invoice payment"],
    "asset": ["Spend money", "Bill payment", "General journal"]
}

# Context-aware transaction descriptions
account_description_map = {
    "ANZ": ["Customer sales deposit", "Supplier payment", "Transfer between accounts", "Owner contribution", "ATO payment"],
    "Business Bank Account #1": ["Customer deposit", "Supplier EFT payment", "Cash withdrawal", "ATO GST payment"],
    "CBA": ["Customer card deposit", "Bill payment", "Owner transfer"],
    "Petty Cash/Cash On Hand": ["Cash sales", "Petty cash for staff meals", "Courier paid in cash"],

    "Trade Debtors": ["Invoice issued to customer", "Customer payment received", "Customer refund applied"],
    "Account receivable": ["Invoice issued to customer", "Customer payment received"],

    "Trade Creditors": ["Supplier invoice received", "Supplier payment made", "Supplier refund received"],
    "ABN Withholdings Payable": ["ABN withholding payable to ATO"],
    "PAYG Withholding Payable": ["PAYG tax withheld from wages", "ATO PAYG payment"],
    "Superannuation Fund #5": ["Employer super contribution", "Superannuation clearing house payment"],
    "Other Payroll Liabilities": ["Payroll deduction for staff"],

    "Inventory": ["Purchase of flour and ingredients", "Purchase of packaging", "Stock adjustment entry"],
    
    "Plant & Equipment": ["Purchase of commercial oven", "Purchase of dough mixer", "Purchase of display fridge", "Equipment upgrade", "Industrial scale purchase"],
    "Motor Vehicle": ["Purchase of delivery van", "Vehicle down payment", "Vehicle trade-in", "Commercial vehicle acquisition"],
    "Office furniture and equipment": ["Purchase of office desk", "Office chairs purchase", "Filing cabinet acquisition", "Computer workstation setup", "Reception counter purchase"],

    "Accounting/Bookkeeping Fees": ["Bookkeeping monthly fee", "Year-end accountant invoice"],
    "Advertising & Marketing": ["Local flyer distribution", "Google ads campaign", "Facebook ad spend"],
    "Bad Debts": ["Customer invoice written off"],
    "Cleaning Expenses": ["Weekly cleaning services", "Window cleaning"],
    "Electricity Expenses": ["Monthly electricity bill"],
    "Gas Expenses": ["Monthly gas bill"],
    "Legal Fees": ["Legal advice consultation"],
    "Parking/Tolls Expenses": ["Delivery van tolls", "Parking fees"],
    "General Repairs & Maintenance": ["Oven repair", "Fridge servicing"],
    "Printing": ["Printing flyers", "Business cards"],
    "Internet": ["Monthly NBN bill"],
    "Computer Expenses": ["Bakery POS software subscription", "Laptop repair"],
    "Council Rates": ["Quarterly council rates bill"],
    "Water Expenses": ["Monthly water bill"],
    "Stationery": ["Office stationery purchase"],
    "Waste Removal": ["Weekly waste collection"],
    "Telephone Expenses": ["Monthly phone bill"],
    "Postage": ["Mailing invoices", "Courier postage"],
    "Freight Out": ["Cake delivery charges"],
    "Late Fees Paid": ["ATO late fee", "Utility late fee"],
    "Discounts Given": ["Discount on cake order"],

    "Wages & Salaries Expenses": ["Weekly staff wages", "Casual staff payment", "Overtime wages"],
    "Work Cover Premiums": ["Work cover insurance premium"],
    "Uniforms": ["Purchase of staff uniforms"],
    "Staff Training Expenses": ["Food safety training course"],
    "Director's Fees": ["Director remuneration"],
    "Travel & Accom. Expenses": ["Hotel stay for bakery expo", "Flight for supplier meeting"],
    "Food": ["Staff meals during overtime"],
    "Mobile Phone Expenses": ["Bakery mobile plan"],
    "Other Payroll Expenses": ["Payroll software subscription"],

    "Furniture Depreciation": ["Annual depreciation - tables/chairs"],
    "Office Equipment Depreciation": ["Annual depreciation - office printer"],
    "Computer Depreciation": ["Annual depreciation - laptops/POS"],
    "Motor Vehicle Depreciation": ["Annual depreciation - delivery van"],
    "Low Value Pool Depreciation": ["Depreciation - small bakery assets"],

    "Motor Vehicle Registration": ["Van registration fee"],
    "Motor Vehicle Insurance": ["Van insurance premium"],
    "Motor Vehicle Fuel/Oil": ["Diesel fuel for deliveries", "Oil change"],

    "GST Collected": ["GST collected on sales"],
    "GST Paid": ["GST paid on supplier invoices"],

    "Owner's/Shareholder's Capital": ["Owner capital injection", "Dividend paid"],
    "Interest Income": ["Interest earned on savings account"],
    "Other Income": ["Equipment hire income", "Miscellaneous bakery income"]
}

# Map accounts to type groups
account_type_map = {
    "bank": ["ANZ", "Business Bank Account #1", "CBA", "Petty Cash/Cash On Hand", "Electronic Clearing Account", "Payroll Clearing Account"],
    "receivable": ["Trade Debtors", "Account receivable"],
    "payable": ["Trade Creditors", "ABN Withholdings Payable", "PAYG Withholding Payable", "Superannuation Fund #5", "Other Payroll Liabilities"],
    "expense": [a for a in unique_accounts if "Expenses" in a or "Fees" in a or "Depreciation" in a or "Training" in a or "Uniforms" in a or "Premiums" in a],
    "income": ["Interest Income", "Other Income"],
    "equity": ["Owner's/Shareholder's Capital"],
    "tax": ["GST Collected", "GST Paid"],
    "asset": ["Inventory", "Plant & Equipment", "Motor Vehicle", "Office furniture and equipment"]
}

# Generate synthetic transactions
dates = pd.date_range(start="2023-07-01", end="2025-06-30", freq="D")
n_samples = 3000
sampled_dates = np.random.choice(dates, n_samples)

rows = []
for i in range(n_samples):
    category = random.choice(unique_accounts)

    # Find account group
    group = next((g for g, accounts in account_type_map.items() if category in accounts), "expense")

    # Select transaction type + description
    t_type = random.choice(transaction_types[group])
    desc = random.choice(account_description_map.get(category, ["General bakery transaction"]))

    open_bal = round(np.random.uniform(500, 20000), 2)
    
    # Apply debit/credit rules based on account type
    if group == "expense" or group == "asset":
        # Expenses and assets: Money Out - debit only, credit = 0
        debit = round(np.random.uniform(50, 5000), 2)  # Non-negative, non-zero
        credit = 0.0
    elif group == "income":
        # Income: Money In - credit only, debit = 0
        debit = 0.0
        credit = round(np.random.uniform(50, 5000), 2)  # Non-zero
    else:
        # Other account types can have both debit and credit
        debit = round(np.random.uniform(0, 5000), 2)
        credit = round(np.random.uniform(0, 5000), 2)
    
    net = debit - credit
    tax = round(random.choice([0, 0.1, 0.2]) * random.uniform(0, 500), 2)

    # Use proper account ID from mapping
    account_id = account_id_mapping[category]

    rows.append([
        sampled_dates[i], account_id, category,
        f"TX{random.randint(10000, 99999)}", t_type, desc,
        open_bal, debit, credit, net, 0.0, tax
    ])

# Build dataframe
df = pd.DataFrame(rows, columns=[
    "Date", "Account Id", "Category", "Reference number",
    "Transaction type", "Transaction description", "Open",
    "Debit", "Credit", "Net Activity", "Balance", "Tax Amount"
])

# Running balances per category
df["Balance"] = df.groupby("Category")["Net Activity"].cumsum() + df["Open"]

# Sort by date
df = df.sort_values("Date").reset_index(drop=True)

# Save
df.to_csv("Synthetic_Bakery_GeneralLedger_prod.csv", index=False)

print("✅ Synthetic Bakery General Ledger CSV created successfully!")
print(df.head())