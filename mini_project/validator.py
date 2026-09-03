"""
Transaction Validator CLI
==========================
Reads transactions from transactions.csv, validates each one using the
functions from checkpoint_test.py (amount validity, ID format, duplicate
IDs, suspicious/high-value flagging), and writes a human-readable report
to report.txt.

Usage:
    python validator.py [input_csv] [output_report]

Defaults to transactions.csv -> report.txt in the current directory.
"""

import csv
import os
import sys

# Make checkpoint_test.py (one directory up) importable regardless of
# where this script is invoked from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from checkpoint_test import (
    is_valid_amount,
    is_valid_transaction_id,
    has_duplicates,
    flag_suspicious,
    generate_summary,
    generate_daily_report,
)


def load_transactions(csv_path):
    """
    Read transactions.csv into a list of dicts.
    Amount is parsed to float where possible; unparsable amounts are kept
    as the original string so they can still be reported as invalid.
    Returns (transactions, row_errors) where row_errors are rows skipped
    entirely due to missing required columns.
    """
    transactions = []
    row_errors = []

    if not os.path.exists(csv_path):
        return transactions, [f"File not found: {csv_path}"]

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_cols = {'id', 'amount', 'date'}
        if reader.fieldnames is None or not required_cols.issubset(set(reader.fieldnames)):
            row_errors.append(
                f"CSV is missing required columns {required_cols}; "
                f"found {reader.fieldnames}"
            )
            return transactions, row_errors

        for i, row in enumerate(reader, start=2):  # header is line 1
            tx_id = (row.get('id') or '').strip()
            date = (row.get('date') or '').strip()
            raw_amount = (row.get('amount') or '').strip()

            if not tx_id:
                row_errors.append(f"Line {i}: missing transaction id, row skipped")
                continue

            try:
                amount = float(raw_amount)
            except ValueError:
                amount = raw_amount  # keep raw so validation flags it as invalid

            transactions.append({'id': tx_id, 'amount': amount, 'date': date})

    return transactions, row_errors


def validate_transactions(transactions):
    """
    Run every transaction through the checkpoint validators.
    Returns a dict of validation results.
    """
    invalid_amount = [t for t in transactions if not is_valid_amount(t['amount'])]
    invalid_id = [t for t in transactions if not is_valid_transaction_id(t['id'])]

    all_ids = [t['id'] for t in transactions]
    duplicate_ids = sorted({tid for tid in all_ids if all_ids.count(tid) > 1})
    has_dupes = has_duplicates(all_ids)

    # Suspicious flagging only makes sense on transactions with a numeric
    # amount, so filter those first.
    numeric_transactions = [t for t in transactions if isinstance(t['amount'], (int, float))]
    suspicious = flag_suspicious(numeric_transactions)

    summary = generate_summary(numeric_transactions)

    return {
        'invalid_amount': invalid_amount,
        'invalid_id': invalid_id,
        'has_duplicates': has_dupes,
        'duplicate_ids': duplicate_ids,
        'suspicious': suspicious,
        'summary': summary,
        'numeric_transactions': numeric_transactions,
    }


def build_report(csv_path, transactions, row_errors, results):
    lines = []
    lines.append("=" * 60)
    lines.append("TRANSACTION VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Source file: {csv_path}")
    lines.append(f"Total rows read: {len(transactions)}")
    lines.append("")

    if row_errors:
        lines.append("-- Row-level errors --")
        for err in row_errors:
            lines.append(f"  ! {err}")
        lines.append("")

    lines.append("-- Amount validation (must be between 1 and 10000) --")
    if results['invalid_amount']:
        for t in results['invalid_amount']:
            lines.append(f"  INVALID  {t['id']}: amount={t['amount']!r}")
    else:
        lines.append("  All amounts valid.")
    lines.append("")

    lines.append("-- Transaction ID format (TX + 3 digits) --")
    if results['invalid_id']:
        for t in results['invalid_id']:
            lines.append(f"  INVALID  {t['id']}")
    else:
        lines.append("  All transaction IDs valid.")
    lines.append("")

    lines.append("-- Duplicate detection --")
    if results['has_duplicates']:
        lines.append(f"  Duplicates found: {', '.join(results['duplicate_ids'])}")
    else:
        lines.append("  No duplicate transaction IDs found.")
    lines.append("")

    lines.append("-- Suspicious transactions (amount > 5000) --")
    if results['suspicious']:
        for t in results['suspicious']:
            lines.append(f"  FLAGGED  {t['id']}: ${t['amount']:.2f} on {t['date']}")
    else:
        lines.append("  No suspicious transactions.")
    lines.append("")

    lines.append("-- Summary statistics (numeric, valid-format amounts only) --")
    s = results['summary']
    lines.append(f"  Count:   {s['count']}")
    lines.append(f"  Total:   ${s['total']:.2f}")
    lines.append(f"  Average: ${s['average']:.2f}")
    lines.append("")

    if results['numeric_transactions']:
        lines.append(generate_daily_report(results['numeric_transactions']))
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(script_dir, 'transactions.csv')
    report_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(script_dir, 'report.txt')

    transactions, row_errors = load_transactions(csv_path)

    if not transactions and not row_errors:
        report_text = (
            "=" * 60 + "\n"
            "TRANSACTION VALIDATION REPORT\n"
            + "=" * 60 + "\n"
            f"Source file: {csv_path}\n"
            "No transactions found in file (file is empty).\n"
            + "=" * 60
        )
    else:
        results = validate_transactions(transactions)
        report_text = build_report(csv_path, transactions, row_errors, results)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text + "\n")

    print(report_text)
    print(f"\nReport written to: {report_path}")


if __name__ == '__main__':
    main()
