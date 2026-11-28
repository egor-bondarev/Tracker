''' Database operations for categories. Every query is limited to one user. '''

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.crud.errors import ConflictError, InvalidCategoryError, NotFoundError
from src.models import models
from src.schemas import schemas


def _own(db: Session, user_id: int):
    return db.query(models.Category).filter(models.Category.user_id == user_id)


def _find(db: Session, category_id: int | None, user_id: int) -> models.Category | None:
    return _own(db, user_id).filter(models.Category.id == category_id).first()


def list_categories(
        db: Session, include_archived: bool = False, *, user_id: int) -> list[models.Category]:
    ''' The user's categories ordered by name. '''

    query = _own(db, user_id)
    if not include_archived:
        query = query.filter(models.Category.archived.is_(False))
    return query.order_by(func.lower(models.Category.name)).all()


def get_category(db: Session, category_id: int, *, user_id: int) -> models.Category:
    ''' Category by id; other users' categories do not exist for this user. '''

    category = _find(db, category_id, user_id)
    if category is None:
        raise NotFoundError(f'Category with id {category_id} does not exist.')
    return category


def require_active_category(db: Session, category_id: int | None, *, user_id: int) -> None:
    ''' A task may be assigned only to the user's existing, not archived category. '''

    if category_id is None:
        return
    category = _find(db, category_id, user_id)
    if category is None or category.archived:
        raise InvalidCategoryError(f'Category with id {category_id} does not exist or is archived.')


def require_existing_category(db: Session, category_id: int | None, *, user_id: int) -> None:
    ''' Queued tasks may keep a category that was archived while they waited. '''

    if category_id is not None and _find(db, category_id, user_id) is None:
        raise InvalidCategoryError(f'Category with id {category_id} does not exist.')


def _commit_name(db: Session, category: models.Category) -> models.Category:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f'Category "{category.name}" already exists.') from exc
    db.refresh(category)
    return category


def create_category(db: Session, item: schemas.CategoryCreate, *, user_id: int) -> models.Category:
    ''' Create a category with a name unique for this user. '''

    category = models.Category(name=item.name, user_id=user_id)
    db.add(category)
    return _commit_name(db, category)


def update_category(
        db: Session, category_id: int, item: schemas.CategoryUpdate, *, user_id: int,
) -> models.Category:
    ''' Rename and/or archive a category; tasks keep their category. '''

    category = get_category(db, category_id, user_id=user_id)
    changes = item.model_dump(exclude_unset=True)
    if changes.get('name') is not None:
        category.name = changes['name']
    if changes.get('archived') is not None:
        category.archived = changes['archived']
    return _commit_name(db, category)


def delete_category(
        db: Session, category_id: int, detach_tasks: bool = False, *, user_id: int) -> None:
    ''' Delete a category. With tasks it needs detach_tasks; the tasks then lose the category. '''

    category = get_category(db, category_id, user_id=user_id)
    tasks = db.query(models.Task).filter(models.Task.category_id == category.id).count()
    if tasks and not detach_tasks:
        raise ConflictError(
            f'Category "{category.name}" has {tasks} tasks. '
            'Archive it, or delete with detach_tasks=true to keep the tasks without a category.')
    db.query(models.Task).filter(models.Task.category_id == category.id)\
        .update({models.Task.category_id: None}, synchronize_session=False)
    db.delete(category)
    db.commit()
