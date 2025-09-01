from __future__ import annotations
import os
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path

from src.db.session import get_db
from src.auth.service import get_current_user
from src.auth.models import User
from src.imports.service import create_import_job, parse_history_pdf_content, commit_import
from src.imports.models import ImportJob
from src.uploads.service import ensure_storage_dir

router = APIRouter(prefix="/imports", tags=["imports"])

@router.post("/history-pdf")
def upload_history_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF is supported for history import")

    job = create_import_job(db, user, source="pdf")
    # save PDF to storage for reproducible parsing
    user_dir = ensure_storage_dir(user)
    pdf_path = user_dir / f"import_{job.id}.pdf"
    content = file.file.read()
    with open(pdf_path, "wb") as f:
        f.write(content)

    rows = parse_history_pdf_content(str(pdf_path))
    if not rows:
        job.status = "failed"
        job.error_message = "No tables found or unable to parse"
        db.add(job)
        db.commit()
        raise HTTPException(status_code=422, detail="Could not parse tables from PDF")

    job.status = "processing"
    job.total_rows = len(rows)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Return a preview (first 50 rows) and job id
    return {"job_id": str(job.id), "preview": rows[:50], "total_rows": len(rows)}

@router.post("/{job_id}/commit")
def commit_history(job_id: str,
    rows: Optional[List[Dict]] = None,  # if provided, commit only these; else re-parse file and commit all
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = db.get(ImportJob, job_id)
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Import job not found")

    # locate stored PDF
    user_dir = ensure_storage_dir(user)
    pdf_path = user_dir / f"import_{job.id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Source PDF not found for job")

    to_commit = rows or parse_history_pdf_content(str(pdf_path))
    if not to_commit:
        raise HTTPException(status_code=422, detail="No rows to commit")

    inserted, failed = commit_import(db, user, job, to_commit)
    return {"job_id": str(job.id), "inserted": inserted, "failed": failed, "total": len(to_commit)}
