''' Database operations for user item. '''

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, not_
from tzlocal import get_localzone
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
            start_timestamp = datetime.now(tz=get_localzone())
        else:
            start_timestamp = datetime.strptime(str(previous_task.finish_timestamp),
                                                "%Y-%m-%d %H:%M:%S.%f")
    except AttributeError:
        start_timestamp = datetime.now()

    duration = _calculate_duration(start_timestamp, item.timestamp)
    db_item = models.Task(
        description=item.description,
        start_timestamp=start_timestamp,
        finish_timestamp=item.timestamp,
        duration=duration)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

def finish_task(db: Session, item: schemas.FinishedTask) -> models.Task:
    ''' Finish task. '''

    task = db.query(models.Task).filter(models.Task.id == item.id).first()

    duration = _calculate_duration(task.start_timestamp, item.timestamp)
    if task:
        task.finish_timestamp = item.timestamp
        task.duration = duration
        db.commit()
        db.refresh(task)
        return task

    return None

def _calculate_duration(start_time, finish_time):
    start_timestamp = datetime.strptime(str(start_time), "%Y-%m-%d %H:%M:%S.%f")
    duration = datetime.strptime(finish_time, "%Y-%m-%d %H:%M:%S.%f") - start_timestamp

    return duration
