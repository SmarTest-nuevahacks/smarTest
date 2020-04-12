import os, sqlite3

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

def add_test(username,name,desc,start_date,end_date,length,group):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute("SELECT MAX(id) FROM tests")
    id=cursor.fetchone()[0]
    print(id)
    cursor.execute('''INSERT INTO tests(name,desc,start_date,end_date,time,teacher,group) VALUES(?,?,?,?,?,?,?)''', (name,desc,start_date,end_date,length,username,group))
    sql="CREATE TABLE IF NOT EXISTS test_questions"+id+"(question_i TEXT, answer_i TEXT, picture_i TEXT)"
    sql1="CREATE TABLE IF NOT EXISTS test_results"+id+"(student TEXT,question_i TEXT, question_j TEXT)"
    cursor.execute(sql)
    cursor.execute(sql1)
    db.commit()
    db.close()
