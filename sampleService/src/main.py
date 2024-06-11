from fastapi import FastAPI
from api import sample

app = FastAPI()

app.include_router(sample.router, prefix="/sample", tags=["sample"])
