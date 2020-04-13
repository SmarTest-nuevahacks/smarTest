import os, sqlite3, random
import datetime

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
    sql="CREATE TABLE IF NOT EXISTS test_questions"+str(id)+"(name TEXT, type TEXT, picture TEXT, answer1 TEXT, answer2 TEXT,answer3 TEXT,answer4 TEXT,correct TEXT, points TEXT)"
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
    string="CREATE TABLE IF NOT EXISTS test_answers"+str(id)+"(student TEXT,"
    for i in range(1,number+1):
        string+="answer"+str(i)+" TEXT"
        if(i<number):
            string+=","
    string+=")"
    print(string)
    return string

def end_add_test(id,number):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute(create_end_test_sql(id,number))
    db.commit()
    db.close()



def sendMessage(username, recipient, header, content):
    date_now=datetime.date.today()
    time_now=datetime.time(datetime.datetime.now().hour,datetime.datetime.now().minute)
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''INSERT INTO messages(sender,recipient,date,time,header,content,read) VALUES(?,?,?,?,?,?,?)''', (username,recipient,date_now,time_now,header,content,"no"))
    db.commit()
    db.close()

def getMessages(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT header,content,date,time FROM messages WHERE recipient=?''', (username,))
    tab=cursor.fetchall()
    db.commit()
    db.close()
    return tab

def getTestName(testId):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT name FROM tests WHERE id=?''', (testId,))
    title = cursor.fetchone()
    db.commit()
    db.close()
    return title[0]

def getPublishedTests(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''SELECT name,desc,start_date,end_date,time,id FROM tests WHERE teacher=?''', (username,))
    tests = cursor.fetchall()
    db.commit()
    db.close()
    return tests

def delete_test(testId):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''DELETE FROM tests WHERE id=?''', (testId,))
    db.commit()
    db.close()