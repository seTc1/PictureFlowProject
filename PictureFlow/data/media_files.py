import datetime
import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class Media(SqlAlchemyBase, UserMixin):
    __tablename__ = 'media_files'

    post_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    post_url = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    post_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    post_description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file_extension = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hiden_post = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    autor_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    autor_ip = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return f'<Media> {self.post_url} {self.post_name}'

