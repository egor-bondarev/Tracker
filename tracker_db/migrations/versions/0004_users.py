"""Add users with per-user tokens; tasks and categories get an owner.

Existing tasks and categories go to a user named "owner" (created only when there is
data to own); issue its token with `python -m tracker_db.users token owner`.
Category names become unique per user instead of globally.

Revision ID: 0004_users
Revises: 0003_task_client_id
Create Date: 2026-11-28
"""
from alembic import op
import sqlalchemy as sa

revision = '0004_users'
down_revision = '0003_task_client_id'
branch_labels = None
depends_on = None

OWNER = 'owner'


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=50), nullable=False, unique=True),
        sa.Column('token_hash', sa.String(length=64), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    for table in ('tasks', 'categories'):
        op.add_column(table, sa.Column('user_id', sa.Integer(), nullable=True))

    bind = op.get_bind()
    has_data = bind.execute(sa.text(
        'SELECT EXISTS (SELECT 1 FROM tasks) OR EXISTS (SELECT 1 FROM categories)')).scalar()
    if has_data:
        owner = bind.execute(
            sa.text('INSERT INTO users (name) VALUES (:name) RETURNING id'), {'name': OWNER},
        ).scalar()
        for table in ('tasks', 'categories'):
            bind.execute(sa.text(f'UPDATE {table} SET user_id = :owner'), {'owner': owner})

    for table in ('tasks', 'categories'):
        op.alter_column(table, 'user_id', nullable=False)
        op.create_foreign_key(f'fk_{table}_user_id_users', table, 'users',
                              ['user_id'], ['id'], ondelete='RESTRICT')
        op.create_index(f'ix_{table}_user_id', table, ['user_id'])

    op.drop_constraint('categories_name_key', 'categories', type_='unique')
    op.create_unique_constraint('uq_categories_user_id_name', 'categories', ['user_id', 'name'])


def downgrade():
    # Fails if two users have categories with the same name: rename them first.
    op.drop_constraint('uq_categories_user_id_name', 'categories', type_='unique')
    op.create_unique_constraint('categories_name_key', 'categories', ['name'])
    for table in ('tasks', 'categories'):
        op.drop_index(f'ix_{table}_user_id', table_name=table)
        op.drop_constraint(f'fk_{table}_user_id_users', table, type_='foreignkey')
        op.drop_column(table, 'user_id')
    op.drop_table('users')
