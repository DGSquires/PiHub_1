from flask import session
from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, ValidationError, RadioField, HiddenField
from wtforms.validators import DataRequired, IPAddress, Email
from ..models import Node, User, Association


# Form to configure Node
class AddNode(Form):
    name = StringField('Reference Label', validators=[DataRequired()])
    ip_address = StringField('IP Address', validators=[DataRequired(), IPAddress()])
    submit = SubmitField('Register Node')

    def validate_name(self, field):
        if Node.query.filter_by(name=field.data).first():
            raise ValidationError('Node with this reference label already exists')

    def validate_ip_address(self, field):
        if Node.query.filter_by(ip_address=field.data).first():
            raise ValidationError('Node with this IP Address already exists')


# Form to add users to Node during it's registration
class AddNodeUsers(Form):
    email = StringField('User Email', validators=[DataRequired(), Email()])
    role = RadioField('User Privilege Level', validators=[DataRequired()],
                      choices=[('STANDARD', 'User'),
                               ('SUPER', 'Super User'),])
    iterate = BooleanField('Add More Users To Node', default=False)
    submit = SubmitField('Add User')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()        # Returns user object from User table
        if user is None:
            raise ValidationError('This email is not registered on this Network')
        node_name = session['node_name']
        node = Node.query.filter_by(name=node_name).first()               # Return the node object form dictionary
        association = Association.query.filter_by(user_id=user.id, node_id=node.id).scalar()
        if association is not None:
            raise ValidationError('This email is already registered to this Node')