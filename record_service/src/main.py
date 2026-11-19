''' Main record_service file. '''

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.api import task
from src.db.session import get_db

app = FastAPI()

app.include_router(task.router, prefix="/add-record", tags=["record_service"])

@app.get("/ready")
def readiness(db: Session = Depends(get_db)):
    """Check access to the tasks table without writing any data."""
    try:
        db.execute(text("SELECT 1 FROM tasks LIMIT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return {"status": "ready"}


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
