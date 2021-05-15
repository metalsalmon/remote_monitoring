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
    version = db.Column(db.String(25))
    connected = db.Column(db.Boolean)

    packages = db.relationship('Package', backref='owner', cascade="all, delete", passive_deletes=True)
    monitors = db.relationship('Monitoring', backref='owner', cascade="all, delete", passive_deletes=True)
    devices = db.relationship('Task', backref='owner', cascade="all, delete", passive_deletes=True)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete = 'SET NULL'), nullable=True)


    def summary(self) -> dict:
        return dict(
            name = self.name,
            ip = self.ip,
            mac = self.mac,
            distribution = self.distribution,
            version = self.version,
            connected = self.connected
        )

    def __repr__(self):
        return '<id %r>' % self.id
