#Database ODM
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, url_for
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# PERMISSIONS DATA STRUCTURE
class Permissions:
    UNLOCK = 0x01
    LOCK = 0x02
    ADD_USER = 0x04
    REMOVE_USER = 0x08
    UNIQUE_ACCESS_TIME = 0x0F


    STANDARD = UNLOCK | LOCK
    SUPER = STANDARD | ADD_USER | REMOVE_USER | UNIQUE_ACCESS_TIME

    permission_dict = {'UNLOCK': UNLOCK, 'LOCK': LOCK, 'ADD_USER': ADD_USER,
                       'REMOVE_USER': REMOVE_USER, 'UNIQUE_ACCESS_TIME':UNIQUE_ACCESS_TIME,
                       'STANDARD': STANDARD, 'SUPER': SUPER}


# NODE-USER ASSOCIATION TABLE
class Association(db.Model):
    __tablename__ = 'Association'
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('Node.id'), primary_key=True)
    permissions = db.Column(db.Integer)

    node = db.relationship('Node')
    user = db.relationship('User')

    def can(self, permisson):
        return self.permissions is not None and \
               (self.permissions & permisson) == permisson

# USER DATA STRUCTURE
class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    nodes = db.relationship('Association')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password) #Returns True if match

    # Generate encrypted token of id using SECRET_KEY
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    # Checks return token by comparing to another generated token
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def accessible_nodes(self):
        return Association.query.filter_by(self.id).all()

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        json_user = {
            'url' : url_for('api.get_user', id=self.id, _external=True),
            'email' : self.email,
            'first_name' : self.first_name,
            'last_name' : self.last_name
        }
        return json_user

# NODE DATA STRUCTURE
class Node(db.Model):
    __tablename__ = 'Node'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    ip_address = db.Column(db.Integer, index=True, unique=True) #Stored as int convert to address using 'ipaddress' module
    dat_start = db.Column(db.String(64), default=None)  #dat = default access time
    dat_end = db.Column(db.String(64), default=None)    #if either = None node is always accessible
    is_open = db.Column(db.Boolean)
    is_online = db.Column(db.Boolean, default=False)     #When raspbery pi's introduced changed to False and make a method to activate
    users = db.relationship('Association')
    permission = db.Column(db.Integer, default=None)

    def to_json(self):
        json_node = {
            'url' : url_for('api.get_node', id=self.id, _external=True),
            'name' : self.name,
            'is_open' : self.is_open
        }
        return json_node
