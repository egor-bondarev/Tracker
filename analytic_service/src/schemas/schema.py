from graphene import ObjectType, Int, String, List, Schema, DateTime
from sqlalchemy.orm import Session
from src.models import models
from src.db import session

class Task(ObjectType):
    id = Int()
    description = String()
    start_timestamp = String()
    finish_timestamp = String()
    duration = String()

    def resolve_duration(self, info):
        return models.format_duration(self.duration)

class Query(ObjectType):
    tasks_in_period = List(Task, start_date=String(required=True), end_date=String(required=True))

    def resolve_tasks_in_period(self, info, start_date, end_date):
        db: Session = session.SessionLocal()
        try:
            return db.query(models.Task).filter(
                models.Task.start_timestamp >= start_date,
                models.Task.finish_timestamp <= end_date
            ).all()
        finally:
            db.close()

schema = Schema(query=Query)
