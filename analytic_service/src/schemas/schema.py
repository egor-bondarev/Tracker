from graphene import Boolean, Field, Int, List, ObjectType, Schema, String
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload
from src.models import models
from src.db import session


class Category(ObjectType):
    id = Int()
    name = String()
    archived = Boolean()


class Task(ObjectType):
    id = Int()
    description = String()
    start_timestamp = String()
    finish_timestamp = String()
    duration = String()
    category_id = Int()
    category = Field(Category)

    def resolve_duration(self, info):
        return models.format_duration(self.duration)


class Query(ObjectType):
    tasks_in_period = List(Task, start_date=String(required=True), end_date=String(required=True))
    categories = List(Category, include_archived=Boolean(default_value=False))

    def resolve_tasks_in_period(self, info, start_date, end_date):
        """Tasks started in the period that finished in it or are still running."""
        db: Session = session.SessionLocal()
        try:
            # The category is loaded eagerly: the session is closed before fields resolve.
            return db.query(models.Task).options(joinedload(models.Task.category)).filter(
                models.Task.start_timestamp >= start_date,
                or_(
                    models.Task.finish_timestamp <= end_date,
                    and_(models.Task.finish_timestamp.is_(None),
                         models.Task.start_timestamp <= end_date),
                ),
            ).order_by(models.Task.start_timestamp, models.Task.id).all()
        finally:
            db.close()

    def resolve_categories(self, info, include_archived):
        db: Session = session.SessionLocal()
        try:
            query = db.query(models.Category)
            if not include_archived:
                query = query.filter(models.Category.archived.is_(False))
            return query.order_by(func.lower(models.Category.name)).all()
        finally:
            db.close()


schema = Schema(query=Query)
