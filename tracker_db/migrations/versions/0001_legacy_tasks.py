"""Baseline: the tasks table as the pre-Alembic initializer created it.

IF NOT EXISTS lets databases created before Alembic adopt this revision without changes.

Revision ID: 0001_legacy_tasks
Revises:
Create Date: 2026-11-26
"""
from alembic import op

revision = '0001_legacy_tasks'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        'CREATE TABLE IF NOT EXISTS tasks ('
        'id SERIAL PRIMARY KEY, start_timestamp VARCHAR, '
        'finish_timestamp VARCHAR, description VARCHAR NOT NULL, duration VARCHAR)'
    )


def downgrade():
    op.drop_table('tasks')
