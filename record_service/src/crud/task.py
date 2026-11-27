''' Database operations for user item. '''

import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, not_
from sqlalchemy.exc import NoResultFound, ArgumentError
from sqlalchemy.exc import IntegrityError
from src.crud.category import require_active_category, require_existing_category
from src.crud.errors import InvalidTimeRangeError, NotFoundError
from src.models import models
from src.schemas import schemas

def create_task(db: Session, item: schemas.NewTask) -> models.Task:
    ''' Create new task. '''

    require_active_category(db, item.category_id)
    db_item = models.Task(
        description=item.description, start_timestamp=item.timestamp,
        category_id=item.category_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

def create_finished_task(db: Session, item: schemas.NewTask) -> models.Task:
    ''' Finish task without creating. '''

    require_active_category(db, item.category_id)
    previous_task = db.query(models.Task).filter(not_(models.Task.finish_timestamp.is_(None)))\
        .order_by(desc(models.Task.finish_timestamp)).first()
    if previous_task is None:
        start_timestamp = datetime.now().replace(microsecond=0)
    else:
        start_timestamp = previous_task.finish_timestamp
    _require_valid_range(start_timestamp, item.timestamp)

    db_item = models.Task(
        description=item.description,
        start_timestamp=start_timestamp,
        finish_timestamp=item.timestamp,
        category_id=item.category_id)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

def finish_task(db: Session, item: schemas.FinishedTask) -> models.Task:
    ''' Finish task. '''

    task = db.query(models.Task).filter(models.Task.id == item.id).first()

    if task:
        if not task.finish_timestamp:
            _require_valid_range(task.start_timestamp, item.timestamp)
            task.finish_timestamp = item.timestamp
            db.commit()
            db.refresh(task)
            return task

        raise ArgumentError(f"Task with id {item.id} already finished.")

    raise NoResultFound(f'Task with id {item.id} is not exist.')


def _require_valid_range(start, finish) -> None:
    if start is not None and finish is not None and finish < start:
        raise InvalidTimeRangeError('Finish time is before start time.')


def get_task(db: Session, task_id: int) -> models.Task:
    ''' Task by id. '''

    found = db.get(models.Task, task_id)
    if found is None:
        raise NotFoundError(f'Task with id {task_id} does not exist.')
    return found


def get_active_task(db: Session) -> models.Task | None:
    ''' The most recently started task that is not finished yet. '''

    return db.query(models.Task).filter(models.Task.finish_timestamp.is_(None))\
        .order_by(desc(models.Task.start_timestamp), desc(models.Task.id)).first()


def update_task(db: Session, task_id: int, item: schemas.TaskUpdate) -> models.Task:
    ''' Change the fields present in the request. '''

    found = get_task(db, task_id)
    changes = item.model_dump(exclude_unset=True)
    if 'category_id' in changes and changes['category_id'] != found.category_id:
        require_active_category(db, changes['category_id'])
    _require_valid_range(
        changes.get('start_timestamp', found.start_timestamp),
        changes.get('finish_timestamp', found.finish_timestamp))
    for field, value in changes.items():
        setattr(found, field, value)
    db.commit()
    db.refresh(found)
    return found


def delete_task(db: Session, task_id: int) -> None:
    ''' Delete a task. '''

    db.delete(get_task(db, task_id))
    db.commit()


def sync_task(db: Session, client_id: uuid.UUID, item: schemas.TaskSync) -> tuple[models.Task, bool]:
    ''' Create or replace the task a client identifies by its own id.

    Returns the task and whether it was created. Sending the same state again changes nothing,
    so a client can retry until it sees a response.
    '''

    require_existing_category(db, item.category_id)
    _require_valid_range(item.start_timestamp, item.finish_timestamp)
    values = item.model_dump()
    found = db.query(models.Task).filter(models.Task.client_id == client_id).first()
    created = found is None
    if created:
        found = models.Task(client_id=client_id, **values)
        db.add(found)
    else:
        for field, value in values.items():
            setattr(found, field, value)
    try:
        db.commit()
    except IntegrityError:
        # Another request created the same client_id first: apply this state to it.
        db.rollback()
        found = db.query(models.Task).filter(models.Task.client_id == client_id).one()
        for field, value in values.items():
            setattr(found, field, value)
        db.commit()
        created = False
    db.refresh(found)
    return found, created
