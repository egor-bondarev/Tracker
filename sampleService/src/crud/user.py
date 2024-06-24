''' Database operations for user item. '''
from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from sqlmodel import select

def get_user(db: Session, user_id: int):
    ''' Return user name and id. '''
    #print('_____2222')
    #print(user_id)
    res = db.execute(select(models.User).where(models.User.id == user_id)).one()[0].username
    #print(res.closed)
    #print(res)
    #print(res.closed)
    #print('_________')
    
    return res

def create_user(db: Session, item: schemas.UserCreate) -> models.User:
    ''' Create user by name. '''
    db_item = models.User(username=item.username)
    db.add(db_item)
    #db.flush()
    db.commit()
    db.refresh(db_item)
    #db.merge(db_item, load=True)
    #db.close()
    return db_item
