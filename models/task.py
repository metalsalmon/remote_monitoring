from models.base_model import db
from models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import JSON


class Task(BaseModel):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key = True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id', ondelete = 'CASCADE'), nullable=False)

    ip = db.Column(db.String(30))
    app = db.Column(db.String(50))
    action = db.Column(db.String(25))
    result = db.Column(db.String(50))
    message = db.Column(db.String(100))
    done = db.Column(db.Boolean)
    finished = db.Column(db.DateTime)
    state = db.Column(db.String(20))
    task_message = db.Column(JSON)


    def summary(self) -> dict:
        return dict(
            ip = self.ip,
            app = self.app,
            action = self.action,
            result = self.result,
            message = self.message,
            state = self.state,
            done = self.done,
            created_at = self.created_at,
            finished = self.finished
            
        )

    def __repr__(self):
        return '<id %r>' % self.id
