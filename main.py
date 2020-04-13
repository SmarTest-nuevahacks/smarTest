import os, os.path, random, hashlib, sys, json
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from werkzeug.utils import secure_filename
from login import signup_f, login_f
from functions import *

UPLOAD_FOLDER = '/home/kknopp/Desktop/smarTest/static/test_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '9je0jaj09jk9dkakdwjnjq'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    if isInit():
        if 'username' in session:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('notinit.html')

@app.route('/index')
def index():
    if 'username' in session:
        if isTeacher(session.get('username')):
            if (session.get('editedtest') == None):
                return render_template('teacher.html', username = session.get('username'), test = None)
            else:
                return render_template('teacher.html', username = session.get('username'), test = getTestName(session.get('editedtest')))
        else:
            return render_template('student.html', username = session.get('username'))
    else:
        return redirect(url_for('login'))



#Adding tests by teachers
@app.route('/addtest')
def addtest():
    if 'username' in session:
        if isTeacher(session.get('username')):
            if 'editedtest' in session:
                return render_template('addquestion.html', username = session.get('username'), questionCount = session.get('questioncount'))
            else:
                return render_template('addtest.html', username = session.get('username'))
        else:
            return render_template('student.html', username = session.get('username'))
    else:
        return redirect(url_for('login'))


@app.route('/starttest', methods=['GET', 'POST'])
def starttest():
    name=request.form['name']
    desc=request.form['description']
    start_date=request.form['start_date']
    end_date=request.form['end_date']
    length=request.form['duration']
    group=request.form['type']
    session['editedtest']=start_add_test(session.get('username'),name,desc,start_date,end_date,length,group)
    session['questioncount']=0
    return render_template('addquestion.html', username = session.get('username'))

@app.route('/addquestion', methods=['GET','POST'])
def addquestion():
    if request.method == 'POST':
        # check if the post request has the file part
        newFilename=""
        if 'file1' not in request.files:
            print("aaa")
        file = request.files['file1']
        # if user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            print("bbb")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            newFilename =  newname(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], newFilename))
        name=request.form['name']
        points=request.form['points']
        type=request.form['type']
        option1=request.form['option1']
        option2=request.form['option2']
        option3=request.form['option3']
        option4=request.form['option4']
        correct=request.form['correct']
        id=session.get('editedtest')
        makeQuestion(id,name,type,points,newFilename,option1,option2,option3,option4,correct)
        oldPoints=session.get('questioncount')
        session['questioncount']=oldPoints+1
    return redirect(url_for('addtest'))

#Messages
@app.route('/message')
def message():
    return render_template("messages.html", username=session.get('username'), content=getMessages(session.get('username')))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['password']
        if login_f(username, password):
            session['username'] = username
            session['password'] = password
            return redirect(url_for('main'))
        else:
        	#bad login or passwd
            return render_template('login.html', info="Bad login or password!")

    return render_template('login.html', info = "")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['password']
        name = request.form['name']
        mail = request.form['mail']
        type = request.form['type']
        teacherpasswd = request.form['teacher']
        if signup_f(username,password,name,mail,type,teacherpasswd):
            return redirect(url_for('main'))
        else:
        	#bad username or password
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['username']
    del session['password']
    return redirect('/')

@app.route('/delete_test', methods=['GET', 'POST'])
def delete_test():
    print(session.get('questioncount'))
    end_add_test(session.get('editedtest'),session.get('questioncount')+1)
    del session['editedtest']
    del session['questioncount']
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)
