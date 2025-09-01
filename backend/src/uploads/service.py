from __future__ import annotations
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import pytesseract
from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.uploads.models import Attachment
from src.transactions.models import Transaction
from src.auth.models import User

ALLOWED_MIME = {"image/jpeg", "image/png", "application/pdf"}
STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", "storage"))

TOTAL_PATTERNS = [
    r"total\s*[:\-]?\s*₹?\s*([0-9]+(?:\.[0-9]{1,2})?)",
    r"amount\s*[:\-]?\s*₹?\s*([0-9]+(?:\.[0-9]{1,2})?)",
    r"grand\s*total\s*[:\-]?\s*₹?\s*([0-9]+(?:\.[0-9]{1,2})?)",
]
DATE_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y", "%d %b %Y", "%m/%d/%Y"]

def ensure_storage_dir(user: User) -> Path:
    user_dir = STORAGE_ROOT / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def save_upload_file(user: User, file: UploadFile) -> Tuple[Attachment, bytes]:
    if file.content_type not in ALLOWED_MIME:
        raise ValueError("Unsupported file type")
    content = file.file.read()
    user_dir = ensure_storage_dir(user)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    safe_name = f"{ts}_{file.filename}".replace(" ", "_")
    storage_key = f"{user.id}/{safe_name}"
    dest_path = user_dir / safe_name
    with open(dest_path, "wb") as f:
        f.write(content)
    attachment = Attachment(
        user_id=user.id,
        transaction_id=None,
        file_name=file.filename,
        mime_type=file.content_type,
        size_bytes=len(content),
        storage_key=storage_key,
    )
    return attachment, content

def preprocess_image_for_ocr(image_bytes: bytes) -> np.ndarray:
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # adaptive threshold helps uneven illumination in POS receipts
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY, 15, 12)
    # slight median blur to reduce salt-and-pepper noise
    blur = cv2.medianBlur(thr, 3)
    return blur

def ocr_image_text(img: np.ndarray) -> str:
    # psm 4 = assume a single column of text of variable sizes (line by line)
    config = "--psm 4"
    text = pytesseract.image_to_string(img, config=config)
    return text

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    # lightweight text extraction for text-based PDFs (not scanned)
    # Camelot/PDFMiner rely on embedded text; scanned PDFs need OCR
    try:
        from pdfminer.high_level import extract_text
        return extract_text(pdf_bytes)
    except Exception:
        return ""

def parse_receipt_text(text: str) -> Tuple[Optional[float], Optional[datetime], Optional[str]]:
    # merchant: first reasonable alpha line (not ALL CAPS noise)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    merchant = None
    for l in lines[:8]:
        if re.search(r"[A-Za-z]{3,}", l) and len(l) <= 40:
            merchant = l
            break

    # total amount by regex precedence
    amount = None
    low_text = text.lower().replace(",", "")
    for pat in TOTAL_PATTERNS:
        m = re.search(pat, low_text)
        if m:
            try:
                amount = float(m.group(1))
                break
            except ValueError:
                pass
    # fallback: last currency-like number
    if amount is None:
        m2 = re.findall(r"₹?\s*([0-9]+(?:\.[0-9]{1,2})?)", low_text)
        if m2:
            try:
                amount = float(m2[-1])
            except ValueError:
                amount = None

    # date detection: try multiple common formats
    date = None
    date_candidates = re.findall(r"(\d{1,2}[-/ ]\d{1,2}[-/ ]\d{2,4}|\d{4}-\d{2}-\d{2})", text)
    for d in date_candidates:
        for fmt in DATE_FORMATS:
            try:
                date = datetime.strptime(d.replace(" ", "-").replace("/", "-"), fmt)
                break
            except ValueError:
                continue
        if date:
            break
    return amount, date, merchant

def create_tx_from_receipt(
    db: Session,
    user: User,
    amount: Optional[float],
    occurred_at: Optional[datetime],
    merchant: Optional[str],
) -> Optional[Transaction]:
    if amount is None or occurred_at is None:
        return None
    tx = Transaction(
        user_id=user.id,
        type="expense",
        amount=amount,
        currency="INR",
        category_id=None,
        merchant=merchant,
        notes="Imported from receipt",
        occurred_at=occurred_at,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
