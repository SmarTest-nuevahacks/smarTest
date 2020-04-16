import os, os.path, random, hashlib, sys, json
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from werkzeug.utils import secure_filename
from login import signup_f, login_f
from functions import *
from datetime import date

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
            return render_template(
                'teacher.html',
                username = session.get('username'),
                test = getTest(session.get('editedtest', 'name')),
                published = getPublishedTests(session.get('username')),
                completed = getCompletedTests(session.get('username')),
                checked = getCheckedTests(session.get('username')),
                date = date.today().strftime("%Y-%m-%d"))
        else:
            return render_template(
                'student.html',
                username = session.get('username'),
                full_name = getName(session.get('username')),
                done = checkIfTestsDone(getClassTests(session.get('username'), 'after'),session.get('username')),
                tests = getClassTests(session.get('username'), 'after'),
                pastTests = getClassTests(session.get('username'), 'before'),
                per=getPercentage,
                date = date.today().strftime("%Y-%m-%d"))
    else:
        return redirect(url_for('login'))




#Solving Tests
@app.route('/solvetest/<int:id>')
def solvetest(id):
    test=getTestContent(id,session.get('username'))
    data={'endtime':testEndTime(id)}
    return render_template('test.html', username = session.get('username'), content=test, testid=id, data=data, testName=getTestName(id))

@app.route('/savetestsolve', methods=['GET', 'POST'])
def savetestsolve():
    values=request.form.getlist('answers[]')
    testid=request.form['testid']
    endSolveTest(session.get('username'),values,testid)
    return redirect(url_for('index'))



#Checking Tests
@app.route('/check/<int:id>', methods=['GET','POST'])
def check(id):
    answers=getAnswers(id)
    test=getTestQuestions(id)
    return render_template('checktest.html', username = session.get('username'), answers=answers, testid=id, test=test, testName=getTestName(id), getName=getName)

@app.route('/savecheck', methods=['GET','POST'])
def savecheck():
    id=request.form['testid']
    student=request.form['student']
    questions = request.form.getlist('questions[]')
    points=request.form.getlist('points[]')
    feedback=request.form['feedback']
    savePoints(id,student,questions,points,feedback)
    if(feedback!=''):
        testName=getTestName(id)
        sendMessage("admin",student,"Feedback from test "+str(testName),feedback)
    answers=getAnswers(id)
    test=getTestQuestions(id)
    return render_template('checktest.html', username = session.get('username'), answers=answers, testid=id, test=test, testName=getTestName(id), getName=getName)

@app.route('/checked/<int:id>')
def checked(id):
    checkFinished(id)
    return render_template(
        'teacher.html',
        username = session.get('username'),
        test = getTest(session.get('editedtest', 'name')),
        published = getPublishedTests(session.get('username')),
        completed = getCompletedTests(session.get('username')),
        checked = getCheckedTests(session.get('username')),
        date = date.today().strftime("%Y-%m-%d"))



#Getting Test Results
@app.route('/results/<int:id>', methods=['GET','POST'])
def results(id):
    if(testTaken(id,session.get('username'))):
        answers=getStudentAnswers(id,session.get('username'))
        test=getTestQuestions(id)
        correct=getCorrect(id)
        feedback=getFeedback(id,session.get('username'))
        return render_template('results.html', username = session.get('username'), answers=answers, testid=id, test=test, testName=getTestName(id), correct=correct, feedback=feedback)
    else:
        return redirect(url_for('index'))

#Adding tests by teachers
@app.route('/addtest', methods=['GET', 'POST'])
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
    session['sumpoints']=0
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
        if (session.get('sumpoints') == None):
            session['sumpoints'] = 0
        oldmaxpoints=session.get('sumpoints')
        session['sumpoints']=oldmaxpoints+int(points)
    return redirect(url_for('addtest'))

#Messages
@app.route('/message')
def message():
    return render_template(
        "messages.html",
        username=session.get('username'),
        content=getMessages(session.get('username')),
        users=getUsers())

@app.route('/sendMessageRequest', methods=['GET', 'POST'])
def sendMessageRequest():
    sendMessage(request.args.get('username'), request.args.get(
        'recipient'), request.args.get('header'), request.args.get('content'))
    return redirect(url_for('message'))

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

@app.route('/endAddTest', methods=['GET', 'POST'])
def endAddTest():
    print(session.get('questioncount'))
    end_add_test(session.get('editedtest'),session.get('questioncount')+1,session.get('sumpoints'),session.get('username'))
    del session['editedtest']
    del session['questioncount']
    del session['sumpoints']
    return redirect('/')

@app.route('/unpublishTest', methods=['GET', 'POST'])
def unpublishTest():
    if (session.get('editedtest') == None):
        session['editedtest'] = getTest(request.args.get('testId'))[0]
        session['questioncount'] = getQuestionNumber(request.args.get('testId'))
    return redirect('/')

@app.route('/deleteTest', methods=['GET', 'POST'])
def deleteTest():
    delete_test(request.args.get('testId'))
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)
