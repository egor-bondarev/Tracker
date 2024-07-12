''' Endpoints. '''

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from sqlalchemy.exc import NoResultFound, ArgumentError
from src.db import session
from src.schemas import schemas
from src.crud import task

router = APIRouter()

@router.post(
    path='/new/',
    response_model=schemas.TaskStartedResponse | schemas.TaskFinishedResponse)
def post_new_task(
    new_task: schemas.NewTask,
    is_task_finished: bool=Query(...),
    db: Session=Depends(session.get_db)):
    ''' POST new task. '''

    if isinstance(is_task_finished, bool):
        if is_task_finished:
            return task.create_finished_task(db=db, item=new_task)

        return task.create_task(db=db, item=new_task)

    raise HTTPException(status_code=422, detail='Flag is_task_finished is missing.')

@router.post(path='/finish/', response_model=schemas.TaskFinishedResponse)
def post_finish_task(new_task: schemas.FinishedTask, db: Session=Depends(session.get_db)):
    ''' POST user to db. '''

    try:
        finished_task = task.finish_task(db=db, item=new_task)
    except ArgumentError as exc:
        raise HTTPException(status_code=409, detail=exc.args[0]) from exc
    except NoResultFound as exc:
        raise HTTPException(status_code=404) from exc

    return finished_task
