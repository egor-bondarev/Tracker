from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound
from src.resources.errors import UserNotFound
from src.api import sample

app = FastAPI()

app.include_router(sample.router, prefix="/sample", tags=["sample"])

@app.exception_handler(HTTPException)
def validation_exception_handler(exc: ValidationError):

    # I can add input parameter "request: Request" for flexible logging.
    return JSONResponse(
        status_code=422,
        content={"detail": exc.json()},
    )

@app.exception_handler(HTTPException)
def notfound_exception_handler(request: Request, exc: NoResultFound):

    return JSONResponse(
        status_code=404,
        content={"detail": UserNotFound.DETAIL},)
