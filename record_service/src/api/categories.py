''' Category endpoints. '''

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from src.api.auth import current_user
from src.api.errors import http_errors
from src.crud import category
from src.db import session
from src.models import models
from src.schemas import schemas

router = APIRouter()


@router.get('', response_model=list[schemas.CategoryResponse])
def list_categories(include_archived: bool = False, db: Session = Depends(session.get_db),
                    user: models.User = Depends(current_user)):
    ''' The user's active categories; archived ones too on request. '''
    return category.list_categories(db, include_archived, user_id=user.id)


@router.post('', response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(item: schemas.CategoryCreate, db: Session = Depends(session.get_db),
                    user: models.User = Depends(current_user)):
    ''' Create a category; names are unique per user. '''
    with http_errors():
        return category.create_category(db, item, user_id=user.id)


@router.patch('/{category_id}', response_model=schemas.CategoryResponse)
def update_category(
        category_id: int, item: schemas.CategoryUpdate, db: Session = Depends(session.get_db),
        user: models.User = Depends(current_user)):
    ''' Rename or (un)archive a category. '''
    with http_errors():
        return category.update_category(db, category_id, item, user_id=user.id)


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
        category_id: int, detach_tasks: bool = False, db: Session = Depends(session.get_db),
        user: models.User = Depends(current_user)):
    ''' Delete a category. One with tasks returns 409 unless detach_tasks=true, which keeps
    the tasks without a category. '''
    with http_errors():
        category.delete_category(db, category_id, detach_tasks, user_id=user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
