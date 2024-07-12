''' Database operations for user item. '''

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, not_
from sqlalchemy.exc import NoResultFound, ArgumentError
from src.models import models
from src.schemas import schemas

def create_task(db: Session, item: schemas.NewTask) -> models.Task:
    ''' Create new task. '''

    db_item = models.Task(description=item.description, start_timestamp=item.timestamp)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

def create_finished_task(db: Session, item: schemas.NewTask) -> models.Task:
    ''' Finish task without creating. '''

    previous_task = db.query(models.Task).filter(not_(models.Task.finish_timestamp.is_(None)))\
        .order_by(desc(models.Task.finish_timestamp)).first()
    try:
        if previous_task.finish_timestamp is None:
            start_timestamp = datetime.now().replace(microsecond=0)
        else:
            start_timestamp = datetime.strptime(previous_task.finish_timestamp, "%Y-%m-%d %H:%M:%S")
    except AttributeError:
        start_timestamp = datetime.now().replace(microsecond=0)

    db_item = models.Task(
        description=item.description,
        start_timestamp=start_timestamp,
        finish_timestamp=item.timestamp,
        duration=item.timestamp - start_timestamp)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

def finish_task(db: Session, item: schemas.FinishedTask) -> models.Task:
    ''' Finish task. '''

    task = db.query(models.Task).filter(models.Task.id == item.id).first()

    if task:
        if not task.finish_timestamp:
            task.finish_timestamp = item.timestamp
            task.duration = item.timestamp - \
                datetime.strptime(task.start_timestamp, "%Y-%m-%d %H:%M:%S")
            db.commit()
            db.refresh(task)
            return task

        raise ArgumentError(f"Task with id {item.id} already finished.")

    raise NoResultFound(f'Task with id {item.id} is not exist.')
