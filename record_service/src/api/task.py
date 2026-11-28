''' Endpoints. '''

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from sqlalchemy.exc import NoResultFound, ArgumentError
from src.api.auth import current_user
from src.api.errors import http_errors
from src.db import session
from src.models import models
from src.schemas import schemas
from src.crud import task

router = APIRouter()

# The finished model comes first: pydantic uses the first union member that fits, and a
# started task (no duration) only fits TaskStartedResponse.
@router.post(
    path='/new/',
    response_model=schemas.TaskFinishedResponse | schemas.TaskStartedResponse)
def post_new_task(
    new_task: schemas.NewTask,
    is_task_finished: bool=Query(...),
    db: Session=Depends(session.get_db),
    user: models.User=Depends(current_user)):
    ''' POST new task. '''

    if isinstance(is_task_finished, bool):
        with http_errors():
            if is_task_finished:
                return task.create_finished_task(db=db, item=new_task, user_id=user.id)

            return task.create_task(db=db, item=new_task, user_id=user.id)

    raise HTTPException(status_code=422, detail='Flag is_task_finished is missing.')

@router.post(path='/finish/', response_model=schemas.TaskFinishedResponse)
def post_finish_task(
    new_task: schemas.FinishedTask,
    db: Session=Depends(session.get_db),
    user: models.User=Depends(current_user)):
    ''' POST user to db. '''

    try:
        with http_errors():
            finished_task = task.finish_task(db=db, item=new_task, user_id=user.id)
    except ArgumentError as exc:
        raise HTTPException(status_code=409, detail=exc.args[0]) from exc
    except NoResultFound as exc:
        raise HTTPException(status_code=404) from exc

    return finished_task
