import datetime
from enum import unique

import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Media(SqlAlchemyBase, UserMixin):
    __tablename__ = 'media_files'

    url = sqlalchemy.Column(sqlalchemy.String, primary_key=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    autor = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hiden = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Media> {self.url} {self.name}'
