from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from src.categories.models import Category
from src.categories.schemas import CategoryCreate, CategoryUpdate
from src.auth.models import User

def create_category(db: Session, user: User, payload: CategoryCreate) -> Category:
    cat = Category(user_id=user.id, name=payload.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def list_categories(db: Session, user: User):
    stmt = select(Category).where(Category.user_id == user.id).order_by(Category.name.asc())
    return db.execute(stmt).scalars().all()

def get_category(db: Session, user: User, category_id: UUID) -> Category | None:
    stmt = select(Category).where(Category.id == category_id, Category.user_id == user.id)
    return db.execute(stmt).scalars().first()

def update_category(db: Session, user: User, category: Category, payload: CategoryUpdate) -> Category:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, user: User, category: Category) -> None:
    db.delete(category)
    db.commit()
