from graphene import ObjectType, Int, String, List, Schema
from sqlalchemy.orm import Session
from src.models import models
from src.db import session

class Task(ObjectType):
    id = Int()
    description = String()
    start_timestamp = String()
    finish_timestamp = String()
    duration = String()

class Query(ObjectType):
    tasks = List(Task)

    def resolve_tasks(self, info):
        db: Session = session.SessionLocal()
        task = db.query(models.Task).all()

        return task

schema = Schema(query=Query)
