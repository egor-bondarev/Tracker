from sqlalchemy.orm import Session
from models import models
from schemas import schemas
from sqlmodel import select

def get_item(db: Session, user_id: int):
    return db.execute(select(models.User).where(models.User.id == user_id)).first()

def create_item(db: Session, item: schemas.UserCreate):
    db_item = models.User(username=item.username)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item