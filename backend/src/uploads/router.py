from __future__ import annotations
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.auth.service import get_current_user
from src.auth.models import User
from src.uploads.service import (
    save_upload_file, preprocess_image_for_ocr, ocr_image_text,
    extract_text_from_pdf_bytes, parse_receipt_text, create_tx_from_receipt,
)
from src.uploads.models import Attachment

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/receipt")
def upload_receipt(
    file: UploadFile = File(...),
    auto_create_tx: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        attachment, content = save_upload_file(user, file)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    text = ""
    if file.content_type in {"image/jpeg", "image/png"}:
        img = preprocess_image_for_ocr(content)
        text = ocr_image_text(img)
    elif file.content_type == "application/pdf":
        text = extract_text_from_pdf_bytes(content)
        if not text.strip():
            # Scanned PDFs would require rasterization + OCR; can add pdf2image later
            raise HTTPException(status_code=422, detail="PDF has no embedded text; upload an image receipt")
    else:
        raise HTTPException(status_code=415, detail="Unsupported media type")

    amount, occurred_at, merchant = parse_receipt_text(text)

    tx = None
    if auto_create_tx:
        tx = create_tx_from_receipt(db, user, amount, occurred_at, merchant)
        if tx:
            # link the attachment to transaction
            attachment.transaction_id = tx.id
            db.add(attachment)
            db.commit()
            db.refresh(attachment)

    return {
        "attachment_id": str(attachment.id),
        "parsed": {"amount": amount, "occurred_at": occurred_at.isoformat() if occurred_at else None, "merchant": merchant},
        "transaction_id": str(tx.id) if tx else None,
        "raw_excerpt": text[:1000],
    }
