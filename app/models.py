from flask_login import UserMixin
from flask_security import RoleMixin
from app import db


class UserDB(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    login = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), index=True)
    name = db.Column(db.String(50))
    active = db.Column(db.Boolean())

    roles = db.relationship('RoleDB')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

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
    name = db.Column(db.String(30))

    def __str__(self):
        return self.name


class PlantsDB(db.Model):
    __tablename__ = 'plants'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(30))
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), index=True)

    facilities = db.relationship('FacilitiesDB')

    def __str__(self):
        return self.name
    
    
class ChecksDB(db.Model):
    __tablename__ = 'checks'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    checkup_id = db.Column(db.Integer, db.ForeignKey('checkups.id'), index=True)
    note = db.Column(db.String(255))
    nfc_id = db.Column(db.Integer, db.ForeignKey('nfc_tag.id'), index=True)
    t_check = db.Column(db.DateTime)

    checkups = db.relationship('CheckupsDB')
    nfctag = db.relationship('NfcTagDB')
    
    
class CheckupsDB(db.Model):
    __tablename__ = 'checkups'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    completed = db.Column(db.Boolean)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    t_start = db.Column(db.DateTime)
    t_end = db.Column(db.DateTime)

    routes = db.relationship('RoutesDB')
    users = db.relationship('UserDB')
    
    
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
    nfc_id = db.Column(db.Integer, db.ForeignKey('nfc_tag.id'), index=True)
    order = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    routes = db.relationship('RoutesDB')
    nfctag = db.relationship('NfcTagDB')
    
    
class RoutesDB(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(30))
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), index=True)
    active = db.Column(db.Boolean)

    facilities = db.relationship('FacilitiesDB')

    def __str__(self):
        return self.name
    
    
class ValChecksDB(db.Model):
    __tablename__ = 'val_checks'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    value = db.Column(db.Float)
    param_id = db.Column(db.Integer, db.ForeignKey('val_params.id'), index=True)
    check_id = db.Column(db.Integer, db.ForeignKey('checks.id'), index=True)

    units = db.relationship('ValParamsDB')

    def __str__(self):
        return self.name
    
    
class ValParamsDB(db.Model):
    __tablename__ = 'val_params'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(30))
    unit_id = db.Column(db.Integer, db.ForeignKey('val_units.id'), index=True)
    nfc_id = db.Column(db.Integer, db.ForeignKey('nfc_tag.id'), index=True)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)

    units = db.relationship('ValUnitsDB')
    nfctag = db.relationship('NfcTagDB')
    
    
class ValUnitsDB(db.Model):
    __tablename__ = 'val_units'

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(10))

    def __str__(self):
        return self.name
    