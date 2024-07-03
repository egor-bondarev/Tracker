''' Main record_service file. '''

from fastapi import FastAPI
from src.api import task

app = FastAPI()

app.include_router(task.router, prefix="/add-record", tags=["record_service"])
