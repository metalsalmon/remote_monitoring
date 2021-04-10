from models.base_model import db
from models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import JSON


class Task(BaseModel):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key = True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id', ondelete = 'CASCADE'), nullable=False)

    app = db.Column(db.String(50))
    sequence_number = db.Column(db.Integer)
    action = db.Column(db.String(25))
    result = db.Column(db.String(50))
    message = db.Column(db.String(100))
    done = db.Column(db.Boolean)


    def summary(self) -> dict:
        return dict(
            app = self.app,
            action = self.action,
            result = self.result,
            message = self.message
        )

    def __repr__(self):
        return '<id %r>' % self.id