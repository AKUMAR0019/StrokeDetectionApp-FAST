from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField,TextAreaField,SubmitField,PasswordField,DateField,SelectField
from wtforms.validators import DataRequired,Email,EqualTo,Length,URL

class SignupForm(FlaskForm):
    """Sign up for a user account."""
    email = StringField(
        'Email',
        [
            Email(message='Not a valid email address.'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Please enter a password.")
        ]
    )
    confirm_password = PasswordField(
        'Repeat Password',
        [
            EqualTo(password, message='Passwords must match.')
        ]
    )
    emergency_contact = SelectField(
        'Choose your preffered method of emergency contact when facial paralysis is detected',
        [DataRequired()],
        choices=[
            ('Call 911', 'Text and call an emergency contact')
        ]
    )
    
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    """Log In"""
    email = StringField(
        'Email',
        [
            Email(message='Not a valid email address.'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired(message="Please enter a password")
        ]

    )

    submit = SubmitField('Submit')