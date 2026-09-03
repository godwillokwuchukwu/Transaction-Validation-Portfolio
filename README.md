# Transaction Validation Portfolio

This folder shows one piece of core logic used in three increasingly
real-world contexts: a checkpoint test, a CLI tool, and a web API.

```
day30-checkpoint/
├── README.md
├── checkpoint_test.py       # Core validation logic (the "library")
├── tests/
│   └── test_checkpoint.py   # pytest suite for the core logic
├── mini_project/
│   ├── validator.py         # CLI: imports checkpoint_test.py
│   ├── transactions.csv     # Sample input (includes edge cases)
│   └── report.txt           # Generated output (run validator.py to regenerate)
└── advanced_challenge/
    ├── main.py               # FastAPI: also imports checkpoint_test.py
    └── requirements.txt
```

## How the pieces connect

`checkpoint_test.py` is the single source of truth for validation rules
(valid amount range, valid ID format, duplicate detection, suspicious
flagging, summary stats). Both downstream projects import it directly
rather than re-implementing the rules:

- `mini_project/validator.py` adds **file I/O**: it reads
  `transactions.csv`, runs every row through the checkpoint functions,
  and writes a plain-text report to `report.txt`.
- `advanced_challenge/main.py` adds a **live HTTP interface**: it wraps
  the same `is_valid_amount` / `is_valid_transaction_id` checks in a
  FastAPI endpoint, adds a rule-based fraud score, and returns a
  recommendation (`approve` / `review` / `reject`).

Change a validation rule once in `checkpoint_test.py` and both the CLI
and the API pick it up automatically.

## Running each piece

### 1. Checkpoint tests
```bash
pip install pytest
pytest tests/ -v
```
17/17 tests pass, covering both the happy path and edge cases (empty
lists, invalid amounts, non-string IDs) for all 10 functions.

### 2. Mini project (CLI)
```bash
cd mini_project
python3 validator.py
```
Reads `transactions.csv`, writes `report.txt`, and prints the report to
the console. Verified edge cases:
- **Empty file** → reports "no transactions found" instead of crashing.
- **Invalid amounts** (negative, non-numeric, over 10000) → listed under
  amount validation, excluded from summary stats.
- **Invalid ID format** (e.g. `TX9`) → listed under ID validation.
- **Duplicate IDs** (e.g. `TX002` appearing twice) → flagged explicitly.

You can also point it at a different file:
```bash
python3 validator.py /path/to/other.csv /path/to/other_report.txt
```

### 3. Advanced challenge (API)
```bash
cd advanced_challenge
pip install -r requirements.txt
uvicorn main:app --reload
```
Then:
```bash
curl -X POST http://127.0.0.1:8000/validate-transaction \
     -H "Content-Type: application/json" \
     -d '{"id": "TX001", "amount": 7600, "date": "2026-09-01"}'
```
Returns validation result, a 0–100 fraud score, and a recommendation.
Interactive docs are available at `http://127.0.0.1:8000/docs` once the
server is running.

## Fraud score model (advanced challenge)

The score is a small, explainable rule set (not a trained model), so
it's easy to audit and swap out later:
- Invalid ID format: +30
- Invalid / out-of-range amount: +30
- Amount above 5000: scaled up to +40 as it approaches 10000
- Suspiciously round amount (e.g. exactly 5000): +5

Thresholds: `< 30` → approve, `30–69` → review, `>= 70` → reject.

## Suggested next improvements

- **Logging**: swap `print()` calls in `validator.py` for the `logging`
  module with a rotating file handler.
- **Email report**: send `report.txt` via `smtplib` or a transactional
  email API after each run.
- **Database storage**: persist parsed transactions and validation
  results to SQLite/Postgres instead of (or alongside) `report.txt`.
- **Real fraud model**: replace `compute_fraud_score` in
  `advanced_challenge/main.py` with a trained model behind the same
  function signature — the API contract doesn't need to change.
