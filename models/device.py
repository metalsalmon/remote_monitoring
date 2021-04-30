from models.base_model import db
from models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import JSON


class Device(BaseModel):
    __tablename__ = 'device'

    id = db.Column(db.Integer, primary_key = True)

    name = db.Column(db.String(50))
    ip = db.Column(db.String(20))
    mac = db.Column(db.String(25))
    distribution = db.Column(db.String(30))
    version = db.Column(db.String(20))

    packages = db.relationship('Package', backref='owner')
    monitors = db.relationship('Monitoring', backref='owner')
    devices = db.relationship('Task', backref='owner')


    def summary(self) -> dict:
        return dict(
            name = self.name,
            ip = self.ip,
            mac = self.mac,
            distribution = self.distribution,
            version = self.version
        )

    def __repr__(self):
        return '<id %r>' % self.id
