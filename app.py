from flask import Flask, render_template, request, send_from_directory, url_for, redirect, flash, Blueprint, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from form import *

#INTIALISING APPS 

app = Flask(__name__)
 
import config # contains Uri for database

import models
from models import *  #importing database

##BASE route

@app.route("/")
def home(): 
    return render_template("home.html") 

#REGISTRATION PAGE

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')

        
        error = None
        if not name or len(name) < 2:
            error = 'Name must be at least 2 characters long.'
        elif not username or len(username) < 3:
            error = 'Username must be at least 3 characters long.'
        elif qualification == 'select your Qualififcation':
            error = 'Please select a valid qualification.'
        elif not dob:
            error = 'Date of birth is required.'
        elif not password or len(password) < 6:
            error = 'Password must be at least 6 characters long.'
        elif password != cpassword:
            error = 'Passwords do not match.'

        if error:
            return render_template('register.html', error=error)
        
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists.')

        # Create and save new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, name=name, qualification=qualification, dob=dob)
        db.session.add(new_user)
        db.session.commit()
        session["logged_in"] = True
        session["role"] = 'User'

        return redirect('/userlogin')

    return render_template('register.html', error=None) 

#create admin login page

@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    if request.method=='POST':
        username = request.form.get('admin')
        password = request.form.get('password')
        admin_data = Admin.query.filter_by(username=username).first()
        if admin_data and check_password_hash(admin_data.password, password):
            session["logged_in"] = True
            session["role"] = 'Admin'
            return redirect("/admin_dashboard")
        else:
            error_data = 'Please enter a valid username or password!'
            return render_template('adminlogin.html', error_data=error_data)
    return render_template("adminlogin.html")

#create user login page
@app.route('/userlogin', methods=['GET','POST'])
def userlogin():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = User.query.filter_by(username=username).first()
        if user_data and check_password_hash(user_data.password, password):
            session["logged_in"] = True
            session["qualification"] = user_data.qualification
            session["role"] = 'user'
            session["uid"] = user_data.id
            return redirect("/user_dashboard")
        else:
            error_data = 'Please enter a valid username or password!'
            return render_template('userlogin.html', error_data=error_data)
    return render_template("userlogin.html")


@app.route("/user_dashboard", methods=["GET"])
def user_dashboard():
    data = db.session.query(
    Quiz.id.label("quiz_id"),
    func.count(Question.id).label("question_count"),
    Quiz.date.label("quiz_date"), 
    Quiz.name.label("name"), 
    Quiz.time_duration.label("quiz_duration") ).join(Question, Quiz.id == Question.quiz_id) \
    .group_by(Quiz.id, Quiz.date) \
    .all()
    
    now = datetime.now()
    
    upcoming = []
    past = []
    
    for q in data:
        quiz_datetime = datetime.strptime(q[2], "%Y-%m-%dT%H:%M")
        if quiz_datetime >= now:
            upcoming.append(q)
        else:
            past.append(q)

    
    print(data)
    return render_template("user_dashboard.html", past=past,upcoming=upcoming)
    
#logout page    
@app.route("/logout", methods=["GET"])
def logout():
    if session:
        session.clear()
        return redirect("/")
    return redirect("/")   


#ADMIN DASHBOARD
@app.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
 subject_list=Subject.query.all()
 chapter_list=Chapter.query.all()
 return render_template("admin_dashboard.html", subject=subject_list, chapter=chapter_list)
 



#Create Subject
@app.route("/create_subject", methods=["GET","POST"])
def create_subject():
    if request.method=="POST":
        name=request.form.get("name")
        description=request.form.get("description")
        if name and description:
            new_subject=Subject(name=name,description=description)
            db.session.add(new_subject)
            db.session.commit()
            return redirect("/admin_dashboard")
    return render_template("create_subject.html")

#Create Chapter
@app.route("/create_chapter/<int:id>", methods=["GET","POST"])
def create_chapter(id):
    if request.method=="POST":
        name=request.form.get("name")
        description=request.form.get("description")
        subject_id=request.form.get("subjectid")
        if name and description and subject_id:
            new_chapter=Chapter(name=name,description=description, subject_id=subject_id)
            db.session.add(new_chapter)
            db.session.commit()
            return redirect("/admin_dashboard")
    return render_template("create_chapter.html",id=id)

#admin_quiz
@app.route("/admin_quiz", methods=["GET"])
def admin_quiz():
    data = db.session.query(Quiz,Chapter).join(Chapter,Quiz.chapter_id==Chapter.id).all()
    question = Question.query.all()
    return render_template('admin_quiz.html', data=data, questions=question)

#Create Quiz

@app.route("/create_quiz", methods=["GET", "POST"]) 
def create_quiz():
    if request.method=="POST":
        id=request.form.get("id")
        date=request.form.get("date")
        duration=request.form.get("duration")
        name=request.form.get("name")
        
        if date and id and duration:
            new_quiz= Quiz (chapter_id=id,date=date,time_duration=duration, name=name)
            db.session.add(new_quiz)
            db.session.commit()
            return redirect("/admin_quiz")
    return render_template("create_quiz.html")
    
#create Questions

@app.route("/create_questions", methods=["GET", "POST"]) 
def create_questions():
    if request.method=="POST":
        id=request.form.get("id")
        title=request.form.get("title")
        statement=request.form.get("statement")
        options=request.form.get("options")
        op1=request.form.get("op1")
        op2=request.form.get("op2")
        op3=request.form.get("op3")
        op4=request.form.get("op4")


        if id and title and statement and options and op1 and op2 and op3 and op4 :
            new_question=Question(quiz_id=id,question_title=title, question_statement=statement, correct_option=options,option_1=op1,option_2=op2,option_3=op3,option_4=op4 )
            db.session.add(new_question)
            db.session.commit()
            return redirect("/admin_quiz")
    return render_template("create_questions.html")

#Admin Summary 
@app.route("/admin_summary", methods=["GET"])
def summary():
    # Get all subjects
    subjects = Subject.query.all()
    summary_data = []

    for subject in subjects:
        # Get all chapters under this subject
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        chapter_ids = [c.id for c in chapters]

        # Get all quizzes under these chapters
        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
        quiz_ids = [q.id for q in quizzes]

        # Get all scores under these quizzes
        scores = Score.query.filter(Score.quiz_id.in_(quiz_ids)).all()

        if scores:
            top_score = max(int(score.total_score) for score in scores)
            attempts = len(scores)
        else:
            top_score = 0
            attempts = 0

        summary_data.append({
            "subject": subject.name,
            "topScore": top_score,
            "attempts": attempts
        })

    return render_template("admin_summary.html", admin_data=summary_data)



@app.route("/start-quiz/<int:quiz_id>", methods=["GET", "POST"])
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == "POST":
        total_questions = len(questions)
        correct_count = 0

        for question in questions:
            user_answer = request.form.get(str(question.id))
            print(user_answer)
            if user_answer and int(user_answer) == question.correct_option:
                correct_count += 1

        # Convert score to percentage
        score_percentage = round((correct_count / total_questions) * 100)

        # Save score to DB
        new_score = Score(
            quiz_id=quiz.id,
            user_id=session['uid'],
            total_score=score_percentage,
            time=datetime.now()
        )
        db.session.add(new_score)
        db.session.commit()

        flash(f"You scored {score_percentage}%", "success")
        return redirect(url_for("user_scores"))

    return render_template("start_quiz.html", quiz=quiz, questions=questions)



@app.route("/quiz_scores/<variable>", methods=["GET", "POST"]) 
def scores_quiz(variable):
    return render_template("quiz_scores.html")

@app.route("/user_scores", methods=["GET"])
def user_scores():
    user_id = session["uid"]

    scores = Score.query.filter_by(user_id=user_id).all()
    quiz_results = []

    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)

        quiz_results.append({
            "id": quiz.id,
            "subject": subject.name,
            "chapter": chapter.name,
            "date": quiz.date,
            "score": int(score.total_score),
        })
    highest_score = max(quiz_results, key=lambda x: x['score'])['score'] if quiz_results else 0
    

    return render_template("user_scores.html", quiz_results=quiz_results,highest_score=highest_score)


@app.route("/user_summary", methods=["GET"])
def user_summary():
    user_id = session["uid"]

    # Step 1: Get all quizzes the user has attempted
    user_scores = Score.query.filter_by(user_id=user_id).all()

    # Collect quiz-related data
    subject_data = {}

    for score in user_scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)

        if subject.name not in subject_data:
            subject_data[subject.name] = {
                "scores": [],
                "attempts": 0
            }

        subject_data[subject.name]["scores"].append(int(score.total_score))
        subject_data[subject.name]["attempts"] += 1

    # Prepare data for frontend
    quiz_data = []
    all_scores = []

    for subject, data in subject_data.items():
        avg_score = sum(data["scores"]) / len(data["scores"])
        all_scores.extend(data["scores"])
        quiz_data.append({
            "subject": subject,
            "score": round(avg_score, 2),
            "attempts": data["attempts"]
        })

    total_quizzes = sum([item["attempts"] for item in quiz_data])
    average_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
    highest_score = max(all_scores) if all_scores else 0
    
    print(total_quizzes,average_score,highest_score)
    
    return render_template(
        "user_summary.html",
        quiz_data=quiz_data,
        total_quizzes=total_quizzes,
        average_score=average_score,
        highest_score=highest_score
    )


#edit function for subject chapters
@app.route('/edit/<int:chapter_id>', methods=['POST'])
def edit(chapter_id):
    chapters = Chapter.query.get(chapter_id)                             

    if chapters is None:
        flash('Chapter not found!')
        return redirect('/admin_dashboard')
    

    chapters.name = request.form.get('name')
    db.session.commit()

    return redirect('/admin_dashboard')

#delete function for subject-chapters
@app.route('/delete/<int:chapter_id>', methods=['GET'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)

    if chapter is None:
        flash('Chapter not found!')
        return redirect('/admin_dashboard')

    db.session.delete(chapter)
    db.session.commit()
    
    flash('Chapter deleted successfully!')
    return redirect('/admin_dashboard')


#delete subject from admin dashboard

@app.route("/delete_subject/<int:subject_id>")
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)

    if subject:
        Chapter.query.filter_by(subject_id=subject_id).delete()  # Delete chapters
        db.session.delete(subject)  # Delete subject
        db.session.commit()

    return redirect(url_for('admin_dashboard'))  # Redirect to dashboard

#delete quiz from a admin dashboard
@app.route("/delete_quiz/<int:quiz_id>")
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)

    if quiz:
        Question.query.filter_by(quiz_id=quiz_id).delete()  # Delete associated questions
        db.session.delete(quiz)  # Delete the quiz itself
        db.session.commit()

    return redirect(url_for('admin_quiz'))  # Redirect to quiz management page

#edit and delete function for quiz question title

@app.route("/edit_question/<int:question_id>")
def edit_question(question_id):
    new_title = request.args.get("new_title")
    question = Question.query.get(question_id)
    if question and new_title:
        question.question_statement = new_title
        db.session.commit()
    return redirect(url_for("admin_quiz"))

@app.route("/delete_question/<int:question_id>")
def delete_question(question_id):
    question = Question.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
    return redirect(url_for("admin_quiz"))




#Admin search function 

@app.route('/admin_search', methods=['GET', 'POST'])
def admin_search():
    if session["role"] != 'Admin':
        return redirect(url_for('/logout'))  # or any safe fallback

    if request.method == 'POST':
        keyword = request.form['query']
        users = User.query.filter(User.username.ilike(f"%{keyword}%")).all()
        subjects = Subject.query.filter(Subject.name.ilike(f"%{keyword}%")).all()
        quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{keyword}%")).all()

        return render_template('admin_search.html', users=users, subjects=subjects, quizzes=quizzes, keyword=keyword)
    
    return render_template('admin_search.html', users=None, subjects=None, quizzes=None)

# user search
@app.route('/usersearch', methods=['GET', 'POST'])
def user_search():
    if request.method == 'POST':
        keyword = request.form['query']
        subjects = Subject.query.filter(Subject.name.ilike(f"%{keyword}%")).all()
        quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{keyword}%")).all()

        return render_template('user_search.html', subjects=subjects, quizzes=quizzes, keyword=keyword)
    
    return render_template('user_search.html', users=None, subjects=None, quizzes=None)

@app.route('/quiz_detail/<int:quiz_id>', methods=['GET'])
def quiz_details(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return redirect('/user_dashboard')

    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id) if chapter else None
    question_count = Question.query.filter_by(quiz_id=quiz.id).count()

    data = {
        'id': quiz.id,
        'subject': subject.name if subject else "",
        'chapter': chapter.name if chapter else "",
        'number_of_questions': question_count,
        'scheduled_date': quiz.date,
        'duration': quiz.time_duration
    }
    print(data)
    return render_template('view_quiz.html',data=data)


if __name__ == "__main__":
    app.run(debug=True)





