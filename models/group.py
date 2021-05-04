from models.base_model import db
from models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import JSON


class Group(BaseModel):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key = True)

    name = db.Column(db.String(50))
    devices = db.relationship('Device', backref='owner')


    def summary(self) -> dict:
        return dict(
            name = self.name,

        )

    def __repr__(self):
        return '<id %r>' % self.id
