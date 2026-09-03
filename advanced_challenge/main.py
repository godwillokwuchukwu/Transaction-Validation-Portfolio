"""
Real-Time Fraud Detection API
==============================
FastAPI service that scores a single transaction on submission.

Run:
    uvicorn main:app --reload

Then POST to /validate-transaction, e.g.:
    curl -X POST http://127.0.0.1:8000/validate-transaction \
         -H "Content-Type: application/json" \
         -d '{"id": "TX001", "amount": 7600, "date": "2026-09-01"}'
"""

import os
import sys
from datetime import date as date_type
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

# Reuse the same validation logic as the CLI (checkpoint_test.py, one
# directory up), so both projects share a single source of truth.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from checkpoint_test import is_valid_amount, is_valid_transaction_id  # noqa: E402


app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="Validates a transaction and returns a fraud score and recommendation.",
    version="1.0.0",
)


class TransactionIn(BaseModel):
    id: str = Field(..., description="Transaction ID, e.g. 'TX001'")
    amount: float = Field(..., description="Transaction amount")
    date: Optional[str] = Field(None, description="Transaction date, YYYY-MM-DD")

    @field_validator('date')
    @classmethod
    def date_format_ok(cls, v):
        if v is None:
            return v
        try:
            date_type.fromisoformat(v)
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format")
        return v


class TransactionOut(BaseModel):
    id: str
    amount: float
    valid: bool
    validation_errors: list[str]
    fraud_score: int
    recommendation: str


def compute_fraud_score(tx: TransactionIn, id_ok: bool, amount_ok: bool) -> int:
    """
    Simple, explainable scoring model (0-100, higher = riskier):
      - Invalid ID format:       +30
      - Invalid / out-of-range amount: +30
      - Very high amount (>5000): scaled contribution up to +40
      - Round-number amount (e.g. exactly 1000, 5000): +5 (common in test fraud)
    This is a rule-based stand-in for a real ML model and is meant to be
    swapped out without changing the API contract.
    """
    score = 0

    if not id_ok:
        score += 30
    if not amount_ok:
        score += 30

    if amount_ok:
        if tx.amount > 5000:
            # Scale from 0 (at 5000) to 40 (at 10000, the max valid amount)
            score += min(40, int((tx.amount - 5000) / 5000 * 40))
        if tx.amount % 1000 == 0 and tx.amount > 0:
            score += 5

    return max(0, min(100, score))


def recommend(score: int) -> str:
    if score >= 70:
        return "reject"
    if score >= 30:
        return "review"
    return "approve"


@app.get("/")
def root():
    return {
        "service": "Real-Time Fraud Detection API",
        "endpoints": ["/validate-transaction (POST)", "/health (GET)"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate-transaction", response_model=TransactionOut)
def validate_transaction(tx: TransactionIn):
    id_ok = is_valid_transaction_id(tx.id)
    amount_ok = is_valid_amount(tx.amount)

    errors = []
    if not id_ok:
        errors.append("Transaction ID must be 'TX' followed by 3 digits (e.g. 'TX001').")
    if not amount_ok:
        errors.append("Amount must be between 1 and 10000.")

    score = compute_fraud_score(tx, id_ok, amount_ok)

    return TransactionOut(
        id=tx.id,
        amount=tx.amount,
        valid=(id_ok and amount_ok),
        validation_errors=errors,
        fraud_score=score,
        recommendation=recommend(score),
    )
