''' Task endpoints for reading and correcting tasks. '''

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from src.api.errors import http_errors
from src.crud import task
from src.db import session
from src.schemas import schemas

router = APIRouter()


@router.get('/active', response_model=Optional[schemas.TaskResponse])
def get_active_task(db: Session = Depends(session.get_db)):
    ''' The running task, or null; lets a client resume after a restart. '''
    return task.get_active_task(db)


@router.put('/by-client-id/{client_id}', response_model=schemas.TaskResponse)
def sync_task(client_id: uuid.UUID, item: schemas.TaskSync, response: Response,
              db: Session = Depends(session.get_db)):
    ''' Create or replace a task by the client's id (201 on create, 200 on update). '''
    with http_errors():
        found, created = task.sync_task(db, client_id, item)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return found


@router.get('/{task_id}', response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(session.get_db)):
    ''' Task by id. '''
    with http_errors():
        return task.get_task(db, task_id)


@router.patch('/{task_id}', response_model=schemas.TaskResponse)
def update_task(task_id: int, item: schemas.TaskUpdate, db: Session = Depends(session.get_db)):
    ''' Change description, category or times. '''
    with http_errors():
        return task.update_task(db, task_id, item)


@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(session.get_db)):
    ''' Delete a task. '''
    with http_errors():
        task.delete_task(db, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
