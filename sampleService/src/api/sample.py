from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.config import settings
from sqlmodel import select
from crud import item
#from api.dependencies import get_db

from models import models
from db import session
from schemas import schemas

#models.Base.metadata.create_all(bind=session.engine)

router = APIRouter()

@router.get('/{user_id}')
def test_get(user_id:int, db: Session = Depends(session.get_db)):
    ''' Test GET method. '''
    result = item.get_item(db=db, user_id=user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result

@router.post('/add2db/', response_model=schemas.UserResponse)
def test_post(user: schemas.UserCreate, db: Session = Depends(session.get_db)):
    ''' Test Post method for adding to db. '''

    return item.create_item(db=db, item=user)