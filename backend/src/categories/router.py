from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.session import get_db
from src.auth.service import get_current_user
from src.auth.models import User
from src.categories.schemas import CategoryCreate, CategoryUpdate, CategoryOut
from src.categories.service import (
    create_category, list_categories, get_category, update_category, delete_category
)

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_cat(payload: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_category(db, user, payload)

@router.get("", response_model=list[CategoryOut])
def list_cat(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_categories(db, user)

@router.get("/{category_id}", response_model=CategoryOut)
def get_cat(category_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = get_category(db, user, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return cat

@router.patch("/{category_id}", response_model=CategoryOut)
def patch_cat(category_id: UUID, payload: CategoryUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = get_category(db, user, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return update_category(db, user, cat, payload)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cat(category_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cat = get_category(db, user, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    delete_category(db, user, cat)
    return None
