"""
Tests for checkpoint_test.py. Run with:  pytest tests/ -v
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from checkpoint_test import (
    is_valid_amount,
    has_duplicates,
    flag_suspicious,
    total_daily_volume,
    generate_summary,
    filter_by_date,
    sort_by_amount_desc,
    find_largest_transaction,
    is_valid_transaction_id,
    generate_daily_report,
    sample_transactions,
    sample_ids,
)


# ---- Problem 1 ---------------------------------------------------------
def test_is_valid_amount_true():
    assert is_valid_amount(1500) is True
    assert is_valid_amount(1) is True
    assert is_valid_amount(10000) is True


def test_is_valid_amount_false():
    assert is_valid_amount(0) is False
    assert is_valid_amount(10001) is False
    assert is_valid_amount(-50) is False
    assert is_valid_amount('not a number') is False


# ---- Problem 2 ---------------------------------------------------------
def test_has_duplicates_true():
    assert has_duplicates(sample_ids) is True


def test_has_duplicates_false():
    assert has_duplicates(['TX001', 'TX002', 'TX003']) is False


# ---- Problem 3 ---------------------------------------------------------
def test_flag_suspicious():
    result = flag_suspicious(sample_transactions)
    ids = {t['id'] for t in result}
    assert ids == {'TX003', 'TX005'}


# ---- Problem 4 ---------------------------------------------------------
def test_total_daily_volume():
    assert total_daily_volume(sample_transactions) == 22200


def test_total_daily_volume_empty():
    assert total_daily_volume([]) == 0


# ---- Problem 5 ---------------------------------------------------------
def test_generate_summary():
    summary = generate_summary(sample_transactions)
    assert summary['count'] == 5
    assert summary['total'] == 22200
    assert summary['average'] == 4440.0


def test_generate_summary_empty():
    summary = generate_summary([])
    assert summary == {'count': 0, 'total': 0, 'average': 0}


# ---- Problem 6 ---------------------------------------------------------
def test_filter_by_date():
    result = filter_by_date(sample_transactions, '2026-09-01')
    assert len(result) == 3
    assert all(t['date'] == '2026-09-01' for t in result)


def test_filter_by_date_no_match():
    assert filter_by_date(sample_transactions, '2099-01-01') == []


# ---- Problem 7 ---------------------------------------------------------
def test_sort_by_amount_desc():
    result = sort_by_amount_desc(sample_transactions)
    amounts = [t['amount'] for t in result]
    assert amounts == sorted(amounts, reverse=True)


# ---- Problem 8 ---------------------------------------------------------
def test_find_largest_transaction():
    largest = find_largest_transaction(sample_transactions)
    assert largest['id'] == 'TX005'
    assert largest['amount'] == 9800


def test_find_largest_transaction_empty():
    assert find_largest_transaction([]) is None


# ---- Problem 9 ---------------------------------------------------------
def test_is_valid_transaction_id_true():
    assert is_valid_transaction_id('TX001') is True
    assert is_valid_transaction_id('TX999') is True


def test_is_valid_transaction_id_false():
    assert is_valid_transaction_id('TX01') is False       # too short
    assert is_valid_transaction_id('TXABC') is False       # not digits
    assert is_valid_transaction_id('AB001') is False       # wrong prefix
    assert is_valid_transaction_id(12345) is False         # not a string


# ---- Problem 10 ---------------------------------------------------------
def test_generate_daily_report():
    report = generate_daily_report(sample_transactions)
    assert report == "Daily Report: 5 transactions, Total: $22200, Average: $4440"
