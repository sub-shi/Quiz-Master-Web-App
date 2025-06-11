from dotenv import load_dotenv 
import os
from os import getenv
from app import app
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRICK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRICK_MODIFICATIONS')
app.config['SECRET_KEY']= os.getenv('SECRET_KEY')

#app.py ke ander set up kr rhe .env ka variables 

