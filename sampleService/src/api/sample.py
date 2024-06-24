''' Endpoints. '''
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from crud import user
from db import session
from schemas import schemas
from resources.errors import UserNotFound, EmptyUserNameError
from pydantic import ValidationError

router = APIRouter()

@router.get('/{user_id}')
def test_get(user_id: int, db: Session=Depends(session.get_db)):
    ''' GET user by id. '''
    try:
        result = user.get_user(db=db, user_id=user_id)
        print('+++++++++++++++++')
        print(result)
    except NoResultFound as exc:
        raise HTTPException(status_code=404) from exc
    return result

@router.post('/add2db/', response_model=schemas.UserResponse)
def test_post(username: schemas.UserCreate, db: Session=Depends(session.get_db)):
    ''' POST user to db. '''
    return user.create_user(db=db, item=username)
    # try:
    #     validated_username = schemas.UserCreate(username=username)
    #     return user.create_user(db=db, item=validated_username)
    # except ValidationError as exc:
    #     print('___')
    #     err = exc
    #     print(exc)
    #     print(exc.args)
    #     raise HTTPException(status_code=422, detail='CCC') from exc
        


