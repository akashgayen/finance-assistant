from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import re
from typing import List, Dict, Optional, Tuple

import camelot
from sqlalchemy.orm import Session

from src.imports.models import ImportJob
from src.transactions.models import Transaction
from src.auth.models import User

DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",          # 2025-08-31
    r"\d{2}/\d{2}/\d{4}",          # 31/08/2025
    r"\d{2}-\d{2}-\d{4}",          # 31-08-2025
    r"\d{2}\s\w{3}\s\d{4}",        # 31 Aug 2025
]
AMOUNT_PATTERN = r"-?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?"

def read_tables_from_pdf(path_or_bytes) -> List:
    try:
        tables = camelot.read_pdf(path_or_bytes, flavor="lattice", pages="all")
        if tables.n == 0:
            tables = camelot.read_pdf(path_or_bytes, flavor="stream", pages="all")
        return list(tables)
    except Exception:
        return []

def to_rows(table) -> List[List[str]]:
    df = table.df.replace("\n", " ", regex=True)
    return df.values.tolist()

def guess_columns(headers: List[str]) -> Dict[str, int]:
    cols = {h.lower(): i for i, h in enumerate(headers)}
    mapping = {"date": None, "description": None, "amount": None}
    # simple header matching
    for key in cols:
        if mapping["date"] is None and "date" in key:
            mapping["date"] = cols[key]
        if mapping["amount"] is None and ("amount" in key or "debit" in key or "credit" in key):
            mapping["amount"] = cols[key]
        if mapping["description"] is None and any(k in key for k in ["desc", "details", "narration", "merchant"]):
            mapping["description"] = cols[key]
    # fallback: by content detection later
    return mapping

def parse_date(s: str) -> Optional[datetime]:
    s = s.strip()
    for pat in DATE_PATTERNS:
        if re.search(pat, s):
            # normalize separators
            s2 = s.replace("/", "-").replace("  ", " ")
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d %b %Y"):
                try:
                    return datetime.strptime(s2, fmt)
                except ValueError:
                    continue
    return None

def parse_amount(s: str) -> Optional[float]:
    s2 = s.replace(",", "").replace("₹", "").strip()
    m = re.search(AMOUNT_PATTERN, s2)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None

def normalize_row(row: List[str], mapping: Dict[str, Optional[int]]) -> Optional[Dict]:
    date_str = row[mapping["date"]] if mapping["date"] is not None and mapping["date"] < len(row) else ""
    amount_str = row[mapping["amount"]] if mapping["amount"] is not None and mapping["amount"] < len(row) else ""
    desc = row[mapping["description"]] if mapping["description"] is not None and mapping["description"] < len(row) else "Imported"
    dt = parse_date(date_str)
    amt = parse_amount(amount_str)
    if dt is None or amt is None:
        return None
    kind = "expense" if amt > 0 else "income"  # adjust if statements encode debit/credit differently
    amt_abs = abs(amt)
    return {"occurred_at": dt, "amount": amt_abs, "type": kind, "merchant": desc[:100], "notes": "Imported from PDF"}

def parse_history_pdf_content(pdf_path: str) -> List[Dict]:
    tables = read_tables_from_pdf(pdf_path)
    rows_out: List[Dict] = []
    for t in tables:
        rows = to_rows(t)
        if not rows:
            continue
        headers = rows
        data_rows = rows[1:]
        mapping = guess_columns(headers)
        for r in data_rows:
            norm = normalize_row(r, mapping)
            if norm:
                rows_out.append(norm)
    return rows_out

def create_import_job(db: Session, user: User, source: str = "pdf") -> ImportJob:
    job = ImportJob(user_id=user.id, source=source, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def commit_import(db: Session, user: User, job: ImportJob, rows: List[Dict]) -> Tuple[int, int]:
    inserted = 0
    failed = 0
    for r in rows:
        try:
            tx = Transaction(
                user_id=user.id,
                type=r["type"],
                amount=r["amount"],
                currency="INR",
                category_id=None,
                merchant=r.get("merchant"),
                notes=r.get("notes"),
                occurred_at=r["occurred_at"],
            )
            db.add(tx)
            inserted += 1
        except Exception:
            failed += 1
    db.commit()
    job.status = "completed"
    job.total_rows = len(rows)
    job.inserted_rows = inserted
    job.failed_rows = failed
    db.add(job)
    db.commit()
    db.refresh(job)
    return inserted, failed
