''' Database operations for categories. '''

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.crud.errors import ConflictError, InvalidCategoryError, NotFoundError
from src.models import models
from src.schemas import schemas


def list_categories(db: Session, include_archived: bool = False) -> list[models.Category]:
    ''' Categories ordered by name. '''

    query = db.query(models.Category)
    if not include_archived:
        query = query.filter(models.Category.archived.is_(False))
    return query.order_by(func.lower(models.Category.name)).all()


def get_category(db: Session, category_id: int) -> models.Category:
    ''' Category by id. '''

    category = db.get(models.Category, category_id)
    if category is None:
        raise NotFoundError(f'Category with id {category_id} does not exist.')
    return category


def require_active_category(db: Session, category_id: int | None) -> None:
    ''' A task may be assigned only to an existing, not archived category. '''

    if category_id is None:
        return
    category = db.get(models.Category, category_id)
    if category is None or category.archived:
        raise InvalidCategoryError(f'Category with id {category_id} does not exist or is archived.')


def require_existing_category(db: Session, category_id: int | None) -> None:
    ''' Queued tasks may keep a category that was archived while they waited. '''

    if category_id is not None and db.get(models.Category, category_id) is None:
        raise InvalidCategoryError(f'Category with id {category_id} does not exist.')


def _commit_name(db: Session, category: models.Category) -> models.Category:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f'Category "{category.name}" already exists.') from exc
    db.refresh(category)
    return category


def create_category(db: Session, item: schemas.CategoryCreate) -> models.Category:
    ''' Create a category with a unique name. '''

    category = models.Category(name=item.name)
    db.add(category)
    return _commit_name(db, category)


def update_category(db: Session, category_id: int, item: schemas.CategoryUpdate) -> models.Category:
    ''' Rename and/or archive a category; tasks keep their category. '''

    category = get_category(db, category_id)
    changes = item.model_dump(exclude_unset=True)
    if changes.get('name') is not None:
        category.name = changes['name']
    if changes.get('archived') is not None:
        category.archived = changes['archived']
    return _commit_name(db, category)
