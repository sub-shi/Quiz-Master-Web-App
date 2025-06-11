from flask import Flask, render_template, request, url_for, redirect, flash 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


from app import app 
db=SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
app.app_context().push()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

login_manager.login_view = "userlogin"


class User(db.Model):
    __tablename__="User"
    id = db.Column('user_id', db.Integer, primary_key = True,nullable = False)
    username = db.Column('username', db.String(64), unique = True,nullable = False)
    password= db.Column('password', db.String,nullable = False)
    name= db.Column('name',db.String, nullable = False)
    qualification= db.Column('qualification', db.String,nullable = False)
    dob= db.Column( "dob", db.String,nullable = False)


class Admin(db.Model):
    __tablename__="Admin"
    id =  db.Column('admin_id', db.Integer, primary_key = True,nullable = False)
    username = db.Column('admin_name', db.String, unique = True,nullable = False)
    password = db.Column('admin_password', db.String,nullable = False)

class Subject(db.Model):
    __tablename__= "Subject"
    id = db.Column('subject_id', db.Integer, primary_key = True)
    name= db.Column("subject_name", db.String, unique = True,nullable = False)
    description= db.Column("subject_desc", db.String)

class Chapter(db.Model):
    __tablename__="Chapter"
    id =  db.Column('chapter_id', db.Integer, primary_key= True,nullable = False)
    name = db.Column("chapter_name", db.String, nullable = False)
    description =  db.Column('chapter_desc', db.String,nullable = False)
    subject_id =  db.Column("subject_id", db.Integer,nullable = False)

class Quiz(db.Model):
    __tablename__="Quiz"
    id = db.Column('quiz_id', db.Integer, primary_key = True,nullable = False)
    date= db.Column("quiz_date", db.String,nullable = False) 
    time_duration= db.Column('quiz_time_duration', db.Integer, nullable = False)
    chapter_id = db.Column("chapter_id", db.Integer, nullable = False)
    name = db.Column("quiz_name", db.String, nullable = False)
    
class Question(db.Model):
    __tablename__="Question"
    id =  db.Column('question_id', db.Integer, primary_key = True,nullable = False, autoincrement=True)
    question_statement = db.Column("quiz_ques", db.String, nullable = False)
    question_title = db.Column("question_title", db.String, nullable=False)
    option_1=db.Column('question_opt1', db.String,nullable = True,)
    option_2=db.Column('question_opt2', db.String, nullable = False)
    option_3=db.Column('question_opt3', db.String,nullable = True,)
    option_4=db.Column('question_opt4', db.String,nullable = True)
    correct_option =db.Column("quiz_correct_option", db.Integer, nullable = False)
    quiz_id= db.Column('quiz_id', db.Integer, nullable = False)

class Score(db.Model):
    __tablename__="Score"
    id = db.Column('score_id', db.Integer, primary_key = True, nullable = False)
    total_score = db.Column("quiz_totalscore", db.String,nullable = False)
    quiz_id = db.Column('quiz_total', db.Integer, nullable = False)
    user_id=db.Column('user_id', db.Integer, nullable = False)
    time = db.Column('time_duration', db.Integer, nullable = False)

#CREATE DATABASE IF IT DOESN'T EXIST
with app.app_context():
   db.create_all()
   if not Admin.query.all():
      admin=Admin(username="kash",password=generate_password_hash("1989"))
      db.session.add(admin)
      db.session.commit()