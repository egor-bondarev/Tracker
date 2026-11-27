''' Category endpoints. '''

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.api.errors import http_errors
from src.crud import category
from src.db import session
from src.schemas import schemas

router = APIRouter()


@router.get('', response_model=list[schemas.CategoryResponse])
def list_categories(include_archived: bool = False, db: Session = Depends(session.get_db)):
    ''' Active categories; archived ones too on request. '''
    return category.list_categories(db, include_archived)


@router.post('', response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(item: schemas.CategoryCreate, db: Session = Depends(session.get_db)):
    ''' Create a category; names are unique. '''
    with http_errors():
        return category.create_category(db, item)


@router.patch('/{category_id}', response_model=schemas.CategoryResponse)
def update_category(
        category_id: int, item: schemas.CategoryUpdate, db: Session = Depends(session.get_db)):
    ''' Rename or (un)archive a category. '''
    with http_errors():
        return category.update_category(db, category_id, item)
