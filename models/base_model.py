from flask_sqlalchemy import SQLAlchemy
from api.errors import ApiException
from api import http_status
from abc import abstractmethod
from flask_migrate import Migrate

db = SQLAlchemy()

def initialize_db(app):
    app.app_context().push()
    db.init_app(app)
    #migrate = Migrate(app, db, compare_type=True)
    db.create_all()


class BaseModel(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def get(self, **kwargs):
        try:
            return self.query().filter_by(**kwargs).first()
        except MultipleResultsFound as e:
            raise ApiException(
                f'Multiple results found.',
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                previous=e
            )
        except NoResultFound as e:
            raise ApiException(
                f'No result found.',
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                previous=e
            )

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            raise ApiException(
                f'There was an error creating the record: {self}.',
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                previous=e
            )

    def update(self, params: dict):
        try:
            for key, value in params.items():
                setattr(self, key, value)
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            raise ApiException(
                f'There was an error updating the record: {self}.',
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                previous=e
            )

    def delete(self):
        try:
            setattr(self, 'deleted_at', datetime.now())
            db.session.commit()
        except DatabaseError as e:
            raise ApiException(
                f'There was an error deleting the record: {self}.',
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                previous=e
            )

    def save(self):
        db.session.commit()

    