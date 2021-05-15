from models.base_model import db
from sqlalchemy.dialects.postgresql import JSON
from models.base_model import BaseModel


class Monitoring(BaseModel):
    __tablename__ = 'monitoring'

    id = db.Column(db.Integer, primary_key = True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id', ondelete = 'CASCADE'), nullable=False)

    time = db.Column(db.Time)
    cpu_usage = db.Column(db.DECIMAL)
    ram_usage = db.Column(db.DECIMAL)
    disk_space = db.Column(db.DECIMAL)
    used_disk_space = db.Column(db.DECIMAL)
    cpu_temp = db.Column(db.DECIMAL)


    def summary(self, device_name, ip) -> dict:
        return dict(
            name = device_name,
            ip = ip,
            time=str(self.time),
            cpu_usage=str(self.cpu_usage),
            ram_usage=str(self.ram_usage),
            disk_space=str(self.disk_space),
            used_disk_space=str(self.used_disk_space),            
            cpu_temp=str(self.cpu_temp)
        )


    def __repr__(self):
        return '<id %r>' % self.id
