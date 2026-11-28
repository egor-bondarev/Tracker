"""Manage Tracker users and their tokens.

Run inside the record service container (database settings come from its environment):

    python -m tracker_db.users list
    python -m tracker_db.users add NAME          # prints the new user's token once
    python -m tracker_db.users token NAME        # issues a new token; the old one stops working
    python -m tracker_db.users rename OLD NEW
"""

import argparse
import sys

from sqlalchemy.exc import IntegrityError

from tracker_db.auth import generate_token, hash_token
from tracker_db.models import Category, Task, User


def find(db, name):
    user = db.query(User).filter(User.name == name).first()
    if user is None:
        raise SystemExit(f'No user named {name!r}.')
    return user


def issue_token(db, user):
    token = generate_token()
    user.token_hash = hash_token(token)
    db.commit()
    return token


def main(argv=None, session_factory=None):
    parser = argparse.ArgumentParser(prog='python -m tracker_db.users', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list', help='users with their task and category counts')
    add = commands.add_parser('add', help='create a user and print its token')
    add.add_argument('name')
    token = commands.add_parser('token', help='issue a new token for a user')
    token.add_argument('name')
    rename = commands.add_parser('rename', help='rename a user')
    rename.add_argument('old')
    rename.add_argument('new')
    args = parser.parse_args(argv)

    if session_factory is None:
        from tracker_db.session import SessionLocal as session_factory
    db = session_factory()
    try:
        if args.command == 'list':
            for user in db.query(User).order_by(User.id):
                tasks = db.query(Task).filter(Task.user_id == user.id).count()
                categories = db.query(Category).filter(Category.user_id == user.id).count()
                state = 'token set' if user.token_hash else 'no token'
                print(f'{user.id}\t{user.name}\t{state}\t{tasks} tasks\t{categories} categories')
        elif args.command == 'add':
            name = args.name.strip()
            if not name or len(name) > 50:
                raise SystemExit('A user name needs 1 to 50 characters.')
            user = User(name=name)
            db.add(user)
            try:
                db.flush()
            except IntegrityError:
                raise SystemExit(f'User {name!r} already exists.') from None
            print(issue_token(db, user))
        elif args.command == 'token':
            print(issue_token(db, find(db, args.name)))
        elif args.command == 'rename':
            user = find(db, args.old)
            user.name = args.new.strip()
            try:
                db.commit()
            except IntegrityError:
                raise SystemExit(f'User {args.new!r} already exists.') from None
            print(f'Renamed {args.old!r} to {user.name!r}.')
    finally:
        db.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
