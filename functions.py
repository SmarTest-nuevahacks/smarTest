import os, sqlite3, random
import datetime
from operator import itemgetter
import boto3

client= boto3.client(
    'ses',
    region_name='eu-central-1',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

def isInit():
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    try:
        cursor.execute('''SELECT hash FROM teacher_cred''')
        type = cursor.fetchone()
        if type==None:
            return False
        return True
    except:
        return False

def newname(filename):
    split = os.path.splitext(filename)
    num=random.randint(1,3788544534436)
    return str(num)+str(split[1])


def isTeacher(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT type FROM users WHERE name=?''', (username,))
    type = cursor.fetchone()[0]
    if(type=="teacher" or type=="admin"):
        return True
    else:
        return False


def start_add_test(username,name,desc,start_date,end_date,length,group):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''INSERT INTO tests(name,desc,start_date,end_date,time,teacher,type) VALUES(?,?,?,?,?,?,?)''', (name,desc,start_date,end_date,length,username,group))
    cursor.execute("SELECT MAX(id) FROM tests")
    id=cursor.fetchone()[0]
    sql="CREATE TABLE IF NOT EXISTS test_questions"+str(id)+"(ind INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT, type TEXT, picture TEXT, answer1 TEXT, answer2 TEXT,answer3 TEXT,answer4 TEXT,correct TEXT, points TEXT)"
    cursor.execute(sql)
    db.commit()
    db.close()
    return id

def makeQuestion(id,name,type,points,newFilename,option1,option2,option3,option4,correct):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="INSERT INTO test_questions"+str(id)+"(name,type,picture,answer1,answer2,answer3,answer4,correct,points) VALUES(?,?,?,?,?,?,?,?,?)"
    cursor.execute(sql, (name,type,newFilename,option1,option2,option3,option4,correct,points))
    db.commit()
    db.close()

def create_end_test_sql(id,number):
    string="CREATE TABLE IF NOT EXISTS test_answers"+str(id)+"(student TEXT UNIQUE, feedback TEXT, "
    for i in range(1,number):
        string+="answer"+str(i)+" TEXT, points"+str(i)+" TEXT"
        string+=","
    string+="cheating_video TEXT, cheating_audio TEXT)"
    return string

def end_add_test(id,number,maxpoints,username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute(create_end_test_sql(id,number))
    cursor.execute('''UPDATE tests SET maxpoints=? WHERE id=?''',(maxpoints,id))
    cursor.execute('''UPDATE tests SET checked="no" WHERE id=?''',(id,))
    #Sending informatory messages
    sql="SELECT type FROM tests WHERE id=?"
    cursor.execute(sql,(id,))
    type=cursor.fetchone()[0]
    sql="SELECT name FROM users WHERE type=?"
    cursor.execute(sql,(type,))
    students=cursor.fetchall()
    db.commit()
    db.close()
    for student in students:
        sendMessage("admin",student[0],"New test published by "+getName(username),"Please remember to take your test and prepare thoroughly! Your teacher, "+getName(username)+" has just published a test!")

def sendMessage(username, recipient, header, content):
    date_now=datetime.date.today()
    time_now=datetime.time(datetime.datetime.now().hour,datetime.datetime.now().minute)
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''INSERT INTO messages(sender,recipient,date,time,header,content,read) VALUES(?,?,?,?,?,?,?)''', (username,recipient,str(date_now),str(time_now),header,content,"no"))
    db.commit()
    db.close()
    response = client.send_email(
        Destination={
            'ToAddresses': ['smartest@prudensai.pl'],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': content,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': header,
            },
        },
        Source='smartest@prudensai.pl',
    )

def getMessages(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT date,header,content,sender,recipient,time FROM messages WHERE recipient=? OR sender=?''', (username, username))
    tab=cursor.fetchall()
    db.commit()
    db.close()
    return tab

def getUsers():
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute("SELECT name,full_name,mail,type FROM users")
    users = cursor.fetchall()
    db.commit()
    db.close()
    return users

def getTest(testId, *name):
    if (testId == None):
        return None
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT * FROM tests WHERE id=?''', (testId,))
    test = cursor.fetchone()
    db.commit()
    db.close()
    if (name):
        return test[1]
    return test

def getQuestionNumber(testId):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM test_questions"+testId)
    questions = cursor.fetchall()
    return len(questions)

def getPublishedTests(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT name,desc,start_date,end_date,time,id FROM tests WHERE teacher=? AND end_date >= date('now')''', (username,))
    tests = cursor.fetchall()
    db.commit()
    db.close()
    return tests

def getCompletedTests(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT name,desc,start_date,end_date,time,id FROM tests WHERE teacher=? AND end_date < date('now') AND checked="no"''', (username,))
    tests = cursor.fetchall()
    db.commit()
    db.close()
    return tests

def getTodayTests_student(username):
    today=datetime.date.today()
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT type FROM users WHERE name=?''', (username,))
    type=cursor.fetchone()[0]
    cursor.execute('''SELECT name,desc,time,teacher,id,maxpoints FROM tests WHERE type=? AND start_date=?''', (type,today))
    tests = cursor.fetchall()
    newtests=[]
    for test in tests:
        sql="SELECT * FROM test_answers"+str(test[4])+" WHERE student=?"
        cursor.execute(sql,(username,))
        done=cursor.fetchone()
        if(done==None):
            newtests+=[test]
    db.commit()
    db.close()
    return newtests

def getTestContent(id,username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="SELECT * FROM test_questions"+str(id)
    cursor.execute(sql)
    content = cursor.fetchall()
    sql="INSERT INTO test_answers"+str(id)+"(student) VALUES(?)"
    cursor.execute(sql,(username,))
    db.commit()
    db.close()
    return content

def endSolveTest(username,answers,id,cheating,audio):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    i=0
    for answer in answers:
        sql="SELECT type from test_questions"+str(id)+" WHERE ind=?"
        cursor.execute(sql,(i+1,))
        type=cursor.fetchone()[0]
        sql="UPDATE test_answers"+str(id)+" SET cheating_video=? WHERE student=?"
        cursor.execute(sql,(str(cheating),username))
        sql="UPDATE test_answers"+str(id)+" SET cheating_audio=? WHERE student=?"
        cursor.execute(sql,(str(audio),username))
        if(type=="open" or type=="coding" or type=="drawn"):
            sql="UPDATE test_answers"+str(id)+" SET answer"+str(i+1)+"=? WHERE student=?"
            cursor.execute(sql,(answer,username))
        if(type=="closed"):
            sql="SELECT correct from test_questions"+str(id)+" WHERE ind=?"
            cursor.execute(sql,(i+1,))
            correct_number=cursor.fetchone()[0]
            sql="SELECT answer"+str(correct_number)+" from test_questions"+str(id)+" WHERE ind=?"
            cursor.execute(sql,(i+1,))
            correct=cursor.fetchone()[0]
            if(answer==correct):
                sql="SELECT points from test_questions"+str(id)+" WHERE ind=?"
                cursor.execute(sql,(i+1,))
                points=cursor.fetchone()[0]
            else:
                points=0
            sql="UPDATE test_answers"+str(id)+" SET answer"+str(i+1)+"=?, points"+str(i+1)+"=? WHERE student=?"
            cursor.execute(sql,(answer,str(points),username))
        i+=1
    db.commit()
    db.close()

def getCheckedTests(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute("SELECT name,desc,start_date,end_date,time,id FROM tests WHERE end_date < date('now') AND teacher=? AND checked='yes'",(username,))
    tests = cursor.fetchall()
    print(tests)
    db.commit()
    db.close()
    return tests

def getClassTests(username, abdate):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT type FROM users WHERE name=?''', (username,))
    type=cursor.fetchone()[0]
    if (abdate == 'before'):
        cursor.execute("SELECT name,desc,start_date,end_date,time,id FROM tests WHERE end_date < date('now') AND type=?",(type,))
    else:
        cursor.execute("SELECT name,desc,start_date,end_date,time,id FROM tests WHERE end_date >= date('now') AND type=? AND checked='no'",(type,))
    tests = cursor.fetchall()
    db.commit()
    db.close()
    return tests

def checkIfTestsDone(tests,username):
    finishedTests=[]
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    for test in tests:
        id=test[5]
        sql="SELECT * FROM test_answers"+str(id)+" WHERE student=?"
        cursor.execute(sql,(username,))
        done=cursor.fetchone()
        if(done==None):
            finishedTests.append(False)
        else:
            finishedTests.append(True)
    db.commit()
    db.close()
    return finishedTests

def delete_test(testId):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''DELETE FROM tests WHERE id=?''', (testId,))
    sql="DROP TABLE IF EXISTS test_questions"+str(testId)
    cursor.execute(sql)
    sql="DROP TABLE IF EXISTS test_answers"+str(testId)
    cursor.execute(sql)
    db.commit()
    db.close()

def testEndTime(id):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT time FROM tests WHERE id=?''',(id,))
    length=int(cursor.fetchone()[0])
    return str(datetime.datetime.now()+datetime.timedelta(minutes=length))

def getName(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT full_name FROM users WHERE name=?''',(username,))
    name=cursor.fetchone()[0]
    db.commit()
    db.close()
    return name

def getAnswers(id):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="SELECT * FROM test_answers"+str(id)
    cursor.execute(sql)
    answers=cursor.fetchall()
    return answers

def getStudentAnswers(id,student):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="SELECT * FROM test_answers"+str(id)+" WHERE student=?"
    cursor.execute(sql,(student,))
    answers=cursor.fetchall()
    return answers

def getCorrect(id):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="SELECT correct FROM test_questions"+str(id)
    cursor.execute(sql)
    answers=cursor.fetchall()
    correct=[]
    ind=1
    for answer in answers:
        if(answer[0]):
            sql="SELECT answer"+answer[0]+" FROM test_questions"+str(id)+" WHERE ind=?"
            cursor.execute(sql,(str(ind),))
            i=cursor.fetchone()[0]
            correct.append(i)
        else:
            correct.append('')
        ind+=1
    return correct

def getTestQuestions(id):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="SELECT * FROM test_questions"+str(id)
    cursor.execute(sql)
    content = cursor.fetchall()
    db.commit()
    db.close()
    return content

def savePoints(id,student,questions,points,feedback):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="UPDATE test_answers"+str(id)+" SET feedback=? WHERE student=?"
    cursor.execute(sql,(feedback,student))
    for i in range(0,len(points)):
        if(points[i]!=''):
            questions[i]=str(int(questions[i])+1)
            sql="UPDATE test_answers"+str(id)+" SET points"+str(questions[i])+"=? WHERE student=?"
            cursor.execute(sql,(points[i],student))
    db.commit()
    db.close()

def getTestName(id):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT name FROM tests WHERE id=?''',(id,))
    name=cursor.fetchone()[0]
    db.commit()
    db.close()
    return name

def getFeedback(id,username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="SELECT feedback FROM test_answers"+str(id)+" WHERE student=?"
    cursor.execute(sql,(username,))
    feedback=cursor.fetchone()[0]
    return feedback

def testTaken(id,username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="SELECT * FROM test_answers"+str(id)+" WHERE student=?"
    cursor.execute(sql,(username,))
    test=cursor.fetchone()
    if(test==None):
        return 0
    else:
        return 1

def getPercentage(id,username):
    points=0
    i=1
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    while(1):
        try:
            sql="SELECT points"+str(i)+" FROM test_answers"+str(id)+" WHERE student=?"
            cursor.execute(sql,(username,))
            try:
                point=int(cursor.fetchone()[0])
                points+=point
            except:
                pass
        except:
            break
        i+=1
    sql="SELECT maxpoints FROM tests WHERE id=?"
    cursor.execute(sql,(id,))
    try:
        maxpoints=int(cursor.fetchone()[0])
    except:
        maxpoints=0
    try:
        return ((points*1.0)/maxpoints)*100
    except:
        return 0

def checkFinished(id):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''UPDATE tests SET checked="yes" WHERE id=?''',(id,))
    db.commit()
    db.close()
    return
