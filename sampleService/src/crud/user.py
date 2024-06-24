''' Database operations for user item. '''

from sqlalchemy.orm import Session
from sqlmodel import select
from src.models import models
from src.schemas import schemas

def get_user(db: Session, user_id: int):
    ''' Return user name and id. '''
    res = db.execute(select(models.User).where(models.User.id == user_id)).one()[0].username
    return res

def create_user(db: Session, item: schemas.UserCreate) -> models.User:
    ''' Create user by name. '''
    db_item = models.User(username=item.username)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item
