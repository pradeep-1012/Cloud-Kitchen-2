import wtforms
from flask_wtf import FlaskForm

class RegistrationForm(FlaskForm):
    fname = wtforms.StringField('first_name', [wtforms.validators.Length(min=4, max=25, message="First Name be between 4 and 25 characters")])
    lname = wtforms.StringField('last_name', [wtforms.validators.Length(min=4, max=25, message="Last Name be between 4 and 25 characters")])
    email = wtforms.StringField('email', [wtforms.validators.Length(min=6, max=35, message="Email be between 6 and 35 characters")])
    password = wtforms.PasswordField('password', [wtforms.validators.DataRequired(), wtforms.validators.EqualTo('confirm', message='Passwords must match')
                                                  ])
    confirm = wtforms.PasswordField('confirm')
class UserLoginForm(FlaskForm):
    username=wtforms.StringField('Username')
    password= wtforms.PasswordField('password')