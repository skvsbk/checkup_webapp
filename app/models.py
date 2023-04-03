from flask_login import UserMixin
from flask_security import RoleMixin
from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from sqlalchemy import select


# class UserDB(db.Model, UserMixin):
class UserDB(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), index=True)
    name = db.Column(db.String(100))
    active = db.Column(db.Boolean())

    roles = db.relationship('RoleDB')

    def __str__(self):
        return self.name


class RoleDB(db.Model, RoleMixin):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __str__(self):
        return self.name


class FacilitiesDB(db.Model):
    __tablename__ = 'facilities'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __str__(self):
        return self.name


class PlantsDB(db.Model):
    __tablename__ = 'plants'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(50))
    description_plant = db.Column(db.String(150))
    description_params = db.Column(db.String(150))
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), index=True)

    facilities = db.relationship('FacilitiesDB')

    def __str__(self):
        return self.name
    

class CheckupHeadersDB(db.Model):
    __tablename__ = 'checkup_headers'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    user_id = db.Column(db.Integer, index=True)
    user_name = db.Column(db.String(100))
    facility_id = db.Column(db.Integer, index=True)
    facility_name = db.Column(db.String(50))
    route_id =db. Column(db.Integer, index=True)
    route_name = db.Column(db.String(100))
    time_start = db.Column(db.DateTime)
    time_finish = db.Column(db.DateTime)
    is_complete = db.Column(db.Boolean)


class CheckupDetailsDB(db.Model):
    __tablename__ = 'checkup_details'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    header_id = db.Column(db.Integer, db.ForeignKey('checkup_headers.id'), index=True)
    nfc_serial = db.Column(db.String(14))
    plant_id = db.Column(db.Integer)
    plant_name = db.Column(db.String(50))
    plant_description = db.Column(db.String(150))
    plant_description_params = db.Column(db.String(150))
    val_name = db.Column(db.String(50))
    val_min = db.Column(db.Float)
    val_max = db.Column(db.Float)
    unit_name = db.Column(db.String(50))
    val_fact = db.Column(db.Float)
    time_check = db.Column(db.DateTime)
    note = db.Column(db.String(150))

    checkup_header = db.relationship('CheckupHeadersDB')

    
class NfcTagDB(db.Model):
    __tablename__ = 'nfc_tag'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    nfc_serial = db.Column(db.String(14))
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), index=True)
    active = db.Column(db.Boolean)

    plant = db.relationship('PlantsDB')

    def __str__(self):
        return f'S/N: {self.nfc_serial} - {self.plant}'
    


class RouteLinksDB(db.Model):
    __tablename__ = 'route_links'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), index=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), index=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), index=True)
    order = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    route = db.relationship('RoutesDB')
    plant = db.relationship('PlantsDB')
    facilities = db.relationship('FacilitiesDB')

    #
    # @hybrid_property
    # def facility(self):
    #     """
    #     SELECT facilities.name FROM facilities
    #     JOIN plants ON plants.facility_id = facilities.id
    #     WHERE plants.id = 46
    #     """
    #     q = db.session.query(FacilitiesDB.name.label('facility')).join(PlantsDB).filter(PlantsDB.id == self.plant_id).first()
    #     return q[0]
    #
    # @facility.expression
    # # @classmethod
    # def facility(cls):
    #     p = db.select(FacilitiesDB.name).join(PlantsDB).where(FacilitiesDB.id == cls.plant_id)
    #     return p


    
class RoutesDB(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(100))
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), index=True)
    active = db.Column(db.Boolean)

    facilities = db.relationship('FacilitiesDB')

    def __str__(self):
        return self.name

    
class ValParamsDB(db.Model):
    __tablename__ = 'val_params'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(50))
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), index=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('val_units.id'), index=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), index=True)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)

    units = db.relationship('ValUnitsDB')
    plant = db.relationship('PlantsDB')
    facility = db.relationship('FacilitiesDB')
    
    
class ValUnitsDB(db.Model):
    __tablename__ = 'val_units'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __str__(self):
        return self.name
    