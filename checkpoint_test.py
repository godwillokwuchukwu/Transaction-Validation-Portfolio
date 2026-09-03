# =============================================================================
# DAY 30 CHECKPOINT TEST — 10 MIXED PROBLEMS (SOLVED)
# =============================================================================
"""
This module contains the core transaction-validation logic used throughout
the project. It's imported directly by mini_project/validator.py and by
advanced_challenge/main.py, so all three pieces share one source of truth.
"""

from datetime import datetime


# -----------------------------------------------------------------------
# PROBLEM 1: Validate Transaction Amount
# -----------------------------------------------------------------------
def is_valid_amount(amount):
    """Return True if amount is between 1 and 10000 (inclusive)."""
    try:
        return 1 <= float(amount) <= 10000
    except (TypeError, ValueError):
        return False


# -----------------------------------------------------------------------
# PROBLEM 2: Check for Duplicate Transactions
# -----------------------------------------------------------------------
def has_duplicates(transaction_ids):
    """Return True if there are duplicate transaction IDs."""
    return len(transaction_ids) != len(set(transaction_ids))


# -----------------------------------------------------------------------
# PROBLEM 3: Flag Suspicious Transactions
# -----------------------------------------------------------------------
def flag_suspicious(transactions):
    """Return a list of transactions where amount > 5000."""
    return [t for t in transactions if t.get('amount', 0) > 5000]


# -----------------------------------------------------------------------
# PROBLEM 4: Calculate Total Daily Transactions
# -----------------------------------------------------------------------
def total_daily_volume(transactions):
    """Return the sum of all transaction amounts."""
    return sum(t.get('amount', 0) for t in transactions)


# -----------------------------------------------------------------------
# PROBLEM 5: Generate Transaction Summary
# -----------------------------------------------------------------------
def generate_summary(transactions):
    """Return a dict with keys: 'count', 'total', 'average'."""
    count = len(transactions)
    total = total_daily_volume(transactions)
    average = total / count if count else 0
    return {'count': count, 'total': total, 'average': average}


# -----------------------------------------------------------------------
# PROBLEM 6: Filter Transactions by Date
# -----------------------------------------------------------------------
def filter_by_date(transactions, target_date):
    """Return transactions that occurred on target_date ('YYYY-MM-DD')."""
    return [t for t in transactions if t.get('date') == target_date]


# -----------------------------------------------------------------------
# PROBLEM 7: Sort Transactions by Amount (Descending)
# -----------------------------------------------------------------------
def sort_by_amount_desc(transactions):
    """Return a new list sorted from highest to lowest amount."""
    return sorted(transactions, key=lambda t: t.get('amount', 0), reverse=True)


# -----------------------------------------------------------------------
# PROBLEM 8: Find Largest Transaction
# -----------------------------------------------------------------------
def find_largest_transaction(transactions):
    """Return the transaction with the highest amount (or None if empty)."""
    if not transactions:
        return None
    return max(transactions, key=lambda t: t.get('amount', 0))


# -----------------------------------------------------------------------
# PROBLEM 9: Validate Transaction ID Format
# -----------------------------------------------------------------------
def is_valid_transaction_id(tx_id):
    """IDs must be 'TX' followed by exactly 3 digits, e.g. 'TX001'."""
    if not isinstance(tx_id, str) or len(tx_id) != 5:
        return False
    return tx_id.startswith('TX') and tx_id[2:].isdigit()


# -----------------------------------------------------------------------
# PROBLEM 10: Generate Daily Report (String Output)
# -----------------------------------------------------------------------
def generate_daily_report(transactions):
    """
    Return a formatted string report, e.g.:
    "Daily Report: 5 transactions, Total: $15000, Average: $3000"
    """
    summary = generate_summary(transactions)
    return (
        f"Daily Report: {summary['count']} transactions, "
        f"Total: ${summary['total']:.0f}, "
        f"Average: ${summary['average']:.0f}"
    )


# =============================================================================
# TEST DATA
# =============================================================================
sample_transactions = [
    {'id': 'TX001', 'amount': 1500, 'date': '2026-09-01'},
    {'id': 'TX002', 'amount': 3200, 'date': '2026-09-01'},
    {'id': 'TX003', 'amount': 7500, 'date': '2026-09-01'},
    {'id': 'TX004', 'amount': 200, 'date': '2026-09-02'},
    {'id': 'TX005', 'amount': 9800, 'date': '2026-09-02'},
]
sample_ids = ['TX001', 'TX002', 'TX003', 'TX001']  # Contains duplicate


if __name__ == '__main__':
    print(is_valid_amount(1500))
    print(has_duplicates(sample_ids))
    print(flag_suspicious(sample_transactions))
    print(total_daily_volume(sample_transactions))
    print(generate_summary(sample_transactions))
    print(filter_by_date(sample_transactions, '2026-09-01'))
    print(sort_by_amount_desc(sample_transactions))
    print(find_largest_transaction(sample_transactions))
    print(is_valid_transaction_id('TX001'))
    print(generate_daily_report(sample_transactions))
