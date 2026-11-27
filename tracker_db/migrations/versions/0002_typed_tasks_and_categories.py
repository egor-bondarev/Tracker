"""Store task times as TIMESTAMP, derive duration, add categories.

Legacy rows hold text such as '2026-11-26 10:00:00' (or ISO with 'T'); empty strings
become NULL. A value PostgreSQL cannot parse aborts the migration, leaving data untouched.

Revision ID: 0002_typed_tasks_and_categories
Revises: 0001_legacy_tasks
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa

revision = '0002_typed_tasks_and_categories'
down_revision = '0001_legacy_tasks'
branch_labels = None
depends_on = None


def upgrade():
    columns = {c['name']: c for c in sa.inspect(op.get_bind()).get_columns('tasks')}
    for column in ('start_timestamp', 'finish_timestamp'):
        # Very old databases were created from the ORM model and are already typed.
        if not isinstance(columns[column]['type'], sa.DateTime):
            op.alter_column(
                'tasks', column, type_=sa.DateTime(), existing_type=sa.String(),
                postgresql_using=f"NULLIF({column}, '')::timestamp",
            )
    # Duration is derived from the timestamps from now on.
    if 'duration' in columns:
        op.drop_column('tasks', 'duration')
    op.create_index('ix_tasks_id', 'tasks', ['id'], if_not_exists=True)
    op.create_index('ix_tasks_start_timestamp', 'tasks', ['start_timestamp'], if_not_exists=True)

    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=50), nullable=False, unique=True),
        sa.Column('archived', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column('tasks', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_tasks_category_id_categories', 'tasks', 'categories',
        ['category_id'], ['id'], ondelete='SET NULL',
    )


def downgrade():
    op.drop_constraint('fk_tasks_category_id_categories', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'category_id')
    op.drop_table('categories')
    op.drop_index('ix_tasks_start_timestamp', table_name='tasks')
    op.drop_index('ix_tasks_id', table_name='tasks')
    op.add_column('tasks', sa.Column('duration', sa.String(), nullable=True))
    op.execute(
        'UPDATE tasks SET duration = (finish_timestamp - start_timestamp)::text '
        'WHERE finish_timestamp IS NOT NULL AND start_timestamp IS NOT NULL'
    )
    for column in ('start_timestamp', 'finish_timestamp'):
        op.alter_column(
            'tasks', column, type_=sa.String(), existing_type=sa.DateTime(),
            postgresql_using=f'{column}::text',
        )
