from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.html5 import EmailField
from flask_login import current_user
from wtforms.validators import InputRequired, EqualTo, Email, Length, Regexp, ValidationError, Optional, DataRequired

from app.models import User, Post


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Submit')
    login = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(),
                                       Length(4, 20),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must start with a letter and must have only letters, numbers, dots or underscores')])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(6)])
    password2 = PasswordField('Repeat password',
                              validators=[InputRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already registered. Please enter another one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please enter a different one.')


class UpdateInfoForm(FlaskForm):
    username = StringField('New Username',
                           validators=[Optional(), Length(4, 20),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must start with a letter and must have only letters, numbers, dots or underscores')])
    email = EmailField('New Email', validators=[Optional(), Email()])
    picture = FileField('Update Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    password = PasswordField('New Password', validators=[Optional(), Length(6)])
    password2 = PasswordField('Repeat your new password',
                              validators=[EqualTo('password', message='Passwords must match.')])
    currentpassword = PasswordField('Enter your current Password', validators=[InputRequired(), Length(6)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
        else:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
        else:
            raise ValidationError('That username is taken. Please choose a different one.')

class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"placeholder": "Type in your comments here", "style":"width:96%;"} )
    submit = SubmitField('Post')


class PasswordResetRequestForm(FlaskForm):
    email = EmailField('Enter your Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError('There is no such account with that email.')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[Optional(), Length(6)])
    password2 = PasswordField('Repeat your new password',
                              validators=[EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Reset Password')