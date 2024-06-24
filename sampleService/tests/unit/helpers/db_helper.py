""" Helper for working with DB. """

from sqlalchemy.orm import Session
from sqlmodel import select
from sampleService.src.models import models

def db_remove_user(session: Session, user_id: int):
    user = session.execute(select(models.User).where(models.User.id == user_id)).first()[0]

    session.delete(user)
    session.commit()

def db_add_user(session: Session, username: str) -> int:
    db_item = models.User(username=username)

    session.add(db_item)
    session.commit()
    session.refresh(db_item)

    return db_item.id
