from flask import session, flash
from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, RadioField, ValidationError, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, IPAddress, Email, StopValidation, EqualTo
from wtforms_components import TimeField
from ..models import User, Node, Association


class NodeInfoForm(Form):
    name = StringField('Access point name')
    ip_address = StringField('IP address')
    dat_start = StringField('Access start time')
    dat_end = StringField('Access end time')
    submit = SubmitField('Submit')

    def validate_name(self, field):
        node_name = session['node_name']
        if Node.query.filter_by(name=field.data).first():
            if Node.query.filter_by(name=node_name).first():
                return
            raise ValidationError('Node with this reference label already exists')

class UserInfoForm(Form):
    first_name = StringField('First name')
    last_name = StringField('Last name')
    email = StringField('Email')
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            if field.data == session['email']:
                return
            raise ValidationError('Email already registered')

class UserPassword(Form):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddUsers(Form):
    email = StringField('User Email', validators=[DataRequired(), Email()])
    iterate = BooleanField('Add More Users To Node', default=False)
    submit = SubmitField('Add User')

class NodeForm(Form):
    submit = SubmitField('Add Users to Access Point')