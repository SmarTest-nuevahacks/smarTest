import os, sqlite3, random

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
    num=random.randint(1,3788544534)
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

def generate_question_sql():
    pass

def start_add_test(username,name,desc,start_date,end_date,length,group):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute("SELECT MAX(id) FROM tests")
    id=cursor.fetchone()[0]
    print(id)
    cursor.execute('''INSERT INTO tests(name,desc,start_date,end_date,time,teacher,type) VALUES(?,?,?,?,?,?,?)''', (name,desc,start_date,end_date,length,username,group))
    db.commit()
    db.close()
    return id

def end_add_test(username):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    sql="CREATE TABLE IF NOT EXISTS test_questions"+id+"(question_i TEXT, answer_i TEXT, picture_i TEXT)"
    sql1="CREATE TABLE IF NOT EXISTS test_results"+id+"(student TEXT,question_i TEXT, question_j TEXT)"
    cursor.execute(sql)
    cursor.execute(sql1)
    db.commit()
    db.close()
