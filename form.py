from flask_wtf import FlaskForm 
from wtforms import(validators,StringField,PasswordField)

class Adminlogin(FlaskForm):
    username=StringField("enter your unsername", [validators.DataRequired(),])
    password=PasswordField("enter your password",[validators.DataRequired(),])
