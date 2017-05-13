from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in', default=False)
    submit = SubmitField('Log In')


class JoinForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 64),
                                                       Regexp('^[a-zA-Z]*$', 0,'Name must contain only letters')])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64),
                                                     Regexp('^[a-zA-Z]*$', 0,'Name must contain only letters')])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Join Network')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')


