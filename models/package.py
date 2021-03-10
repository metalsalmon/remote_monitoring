from models.base_model import db
from sqlalchemy.dialects.postgresql import JSON
from models.base_model import BaseModel


class Package(BaseModel):
    __tablename__ = 'package'

    id = db.Column(db.Integer, primary_key = True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id', ondelete = 'CASCADE'), nullable=False)

    name = db.Column(db.String(50))
    version = db.Column(db.String(50))

    def __repr__(self):
        return '<id %r>' % self.id
