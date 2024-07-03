''' Endpoints. '''

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db import session
from src.schemas import schemas
from src.crud import task

router = APIRouter()

@router.post('/new/', response_model=(schemas.TaskStartedResponse | schemas.TaskFinishedResponse))
def post_new_task(new_task: schemas.NewTask, db: Session=Depends(session.get_db)):
    ''' POST new task. '''

    if new_task.is_task_finished:
        return task.create_finished_task(db=db, item=new_task)

    return task.create_task(db=db, item=new_task)


@router.post('/finish/', response_model=schemas.TaskFinishedResponse)
def post_finish_task(new_task: schemas.FinishedTask, db: Session=Depends(session.get_db)):
    ''' POST user to db. '''

    return task.finish_task(db=db, item=new_task)
