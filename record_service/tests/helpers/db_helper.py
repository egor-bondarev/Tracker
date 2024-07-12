import uuid

from datetime import timedelta
from sqlalchemy.orm import Session
from sqlmodel import select
from tests.helpers import generators
from src.models import models

def add_full_record(session: Session):
    delta = timedelta(minutes=2)

    db_item = models.Task(
        description=str(uuid.uuid4()),
        start_timestamp=generators.timestamp_now(),
        finish_timestamp=generators.timestamp_now() + delta,
        duration=str(delta))

    session.add(db_item)
    session.commit()
    session.refresh(db_item)

    return db_item

def add_started_record(session: Session):
    db_item = models.Task(
        description=str(uuid.uuid4()),
        start_timestamp=generators.timestamp_now())

    session.add(db_item)
    session.commit()
    session.refresh(db_item)

    return db_item

def remove_record(session: Session, task_id):
    task = session.execute(select(models.Task).where(models.Task.id == task_id)).first()[0]

    session.delete(task)
    session.commit()
