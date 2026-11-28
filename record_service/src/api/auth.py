''' Bearer token authentication: every endpoint except /ready acts for one user. '''

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from tracker_db.auth import hash_token
from src.db import session
from src.models import models


def current_user(
        authorization: str | None = Header(default=None),
        db: Session = Depends(session.get_db)) -> models.User:
    ''' The user whose token is in "Authorization: Bearer <token>"; 401 otherwise. '''

    scheme, _, token = (authorization or '').partition(' ')
    token = token.strip()
    user = None
    if scheme.lower() == 'bearer' and token:
        user = db.query(models.User).filter(models.User.token_hash == hash_token(token)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing or invalid token.',
            headers={'WWW-Authenticate': 'Bearer'})
    return user
