from flask_login import UserMixin
from flask_security import RoleMixin
from app import db


class UserDB(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    login = db.Column(db.String(10), unique=True)
    password = db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.role_id'), index=True)
    name = db.Column(db.String(50))
    active = db.Column(db.Boolean())

    roles = db.relationship('RoleDB')

    def __str__(self):
        return self.name


class RoleDB(db.Model, RoleMixin):
    __tablename__ = 'user_roles'

    role_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(50))

    def __str__(self):
        return self.name


class FacilitiesDB(db.Model):
    __tablename__ = 'facilities'

    facility_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(30))

    def __repr__(self):
        return self.name


class PlantsDB(db.Model):
    __tablename__ = 'plants'

    plant_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(30))
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.facility_id'), index=True)

    facilities = db.relationship('FacilitiesDB')

    def __repr__(self):
        return self.name
    
    
class ChecksDB(db.Model):
    __tablename__ = 'checks'

    check_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    note = db.Column(db.String(256))
    checkup_id = db.Column(db.Integer, db.ForeignKey('checkups.checkup_id'), index=True)
    nfc_id = db.Column(db.Integer, db.ForeignKey('nfc_tag.nfc_id'), index=True)

    checkups = db.relationship('CheckupsDB')
    nfctag = db.relationship('NfcTagDB')
    
    
class CheckupsDB(db.Model):
    __tablename__ = 'checkups'

    checkup_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    completed = db.Column(db.Boolean)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), index=True)
    t_start = db.Column(db.Integer)
    t_end = db.Column(db.Integer)

    routes = db.relationship('RoutesDB')
    user = db.relationship('UserDB')
    
    
class NfcTagDB(db.Model):
    __tablename__ = 'nfc_tag'

    nfc_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    nfc_serial = db.Column(db.String(14))
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'), index=True)

    plant = db.relationship('PlantsDB')
    
    
class RouteLinksDB(db.Model):
    __tablename__ = 'route_links'

    routelink_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), index=True)
    nfc_id = db.Column(db.Integer, db.ForeignKey('nfc_tag.nfc_id'), index=True)
    order = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    routes = db.relationship('RoutesDB')
    nfctag = db.relationship('NfcTagDB')
    
    
class RoutesDB(db.Model):
    __tablename__ = 'routes'

    route_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(30))
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.facility_id'), index=True)
    active = db.Column(db.Boolean)

    facilities = db.relationship('FacilitiesDB')

    def __repr__(self):
        return self.name
    
    
class ValChecksDB(db.Model):
    __tablename__ = 'val_checks'

    valcheck_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    value = db.Column(db.Float)
    note = db.Column(db.String(256))
    param_id = db.Column(db.Integer, db.ForeignKey('val_params.param_id'), index=True)
    check_id = db.Column(db.Integer, db.ForeignKey('checks.check_id'), index=True)

    units = db.relationship('ValParamsDB')

    def __repr__(self):
        return self.name
    
    
class ValParamsDB(db.Model):
    __tablename__ = 'val_params'

    param_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(30))
    unit_id = db.Column(db.Integer, db.ForeignKey('val_units.unit_id'), index=True)
    nfc_id = db.Column(db.Integer, db.ForeignKey('nfc_tag.nfc_id'), index=True)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)

    units = db.relationship('ValUnitsDB')
    nfctag = db.relationship('NfcTagDB')
    
    
class ValUnitsDB(db.Model):
    __tablename__ = 'val_units'

    unit_id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(10))

    def __repr__(self):
        return self.name
    