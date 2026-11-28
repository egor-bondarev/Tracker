from graphene import Boolean, Field, Int, List, ObjectType, Schema, String
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload
from src.models import models
from src.db import session


class User(ObjectType):
    id = Int()
    name = String()


class Category(ObjectType):
    id = Int()
    user_id = Int()
    name = String()
    archived = Boolean()


class Task(ObjectType):
    id = Int()
    description = String()
    start_timestamp = String()
    finish_timestamp = String()
    duration = String()
    user_id = Int()
    category_id = Int()
    category = Field(Category)

    def resolve_duration(self, info):
        return models.format_duration(self.duration)


class Query(ObjectType):
    """Read-only analytics. Open inside the home network; userId narrows to one user."""
    users = List(User)
    tasks_in_period = List(Task, start_date=String(required=True), end_date=String(required=True),
                           user_id=Int())
    categories = List(Category, include_archived=Boolean(default_value=False), user_id=Int())

    def resolve_users(self, info):
        db: Session = session.SessionLocal()
        try:
            return db.query(models.User).order_by(models.User.id).all()
        finally:
            db.close()

    def resolve_tasks_in_period(self, info, start_date, end_date, user_id=None):
        """Tasks started in the period that finished in it or are still running."""
        db: Session = session.SessionLocal()
        try:
            query = db.query(models.Task)
            if user_id is not None:
                query = query.filter(models.Task.user_id == user_id)
            # The category is loaded eagerly: the session is closed before fields resolve.
            return query.options(joinedload(models.Task.category)).filter(
                models.Task.start_timestamp >= start_date,
                or_(
                    models.Task.finish_timestamp <= end_date,
                    and_(models.Task.finish_timestamp.is_(None),
                         models.Task.start_timestamp <= end_date),
                ),
            ).order_by(models.Task.start_timestamp, models.Task.id).all()
        finally:
            db.close()

    def resolve_categories(self, info, include_archived, user_id=None):
        db: Session = session.SessionLocal()
        try:
            query = db.query(models.Category)
            if user_id is not None:
                query = query.filter(models.Category.user_id == user_id)
            if not include_archived:
                query = query.filter(models.Category.archived.is_(False))
            return query.order_by(func.lower(models.Category.name)).all()
        finally:
            db.close()


schema = Schema(query=Query)
