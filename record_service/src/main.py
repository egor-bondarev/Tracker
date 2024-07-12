''' Main record_service file. '''

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import task

app = FastAPI()

app.include_router(task.router, prefix="/add-record", tags=["record_service"])

@app.exception_handler(HTTPException)
def validation_exception_handler(exc: ValidationError):

    return JSONResponse(
        status_code=422,
        content={"detail": exc.json()},
    )

@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": f"{exc.detail}"},
    )
