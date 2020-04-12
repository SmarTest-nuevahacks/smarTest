import hashlib, os, binascii, sqlite3

def hash(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'),salt.encode('ascii'),100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def insertuser(username,passwd,name,mail,type):
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    cursor.execute('''INSERT INTO users(name,password,full_name,mail,type) VALUES(?,?,?,?,?)''', (username,hash(passwd),name,mail,type))
    db.commit()
    db.close()

def signup_f(username,passwd,name,mail,type,teacherpasswd):
    try:
        if(teacherpasswd==""):
            type="student"
        else:
            db = sqlite3.connect("smartest.db")
            cursor = db.cursor()
            cursor.execute('''SELECT * FROM teacher_cred''')
            stored = cursor.fetchone()[0]
            db.commit()
            db.close()
            if(verify(stored, teacherpasswd)):
                type="teacher"
            else:
                return False
        insertuser(username,passwd,name,mail,type)
    except:
        return False
    return True

def login_f(user, passwd):
    if passwd == "":
        return False
    db = sqlite3.connect("smartest.db")
    cursor = db.cursor()
    #cursor.execute('''SELECT password, verfied FROM users WHERE name=?''', (user,))
    cursor.execute('''SELECT password FROM users WHERE name=?''', (user,))
    users = cursor.fetchone()
    if users == None:
        return False
    #if users[1]==0:
    #    return False
    user1=users[0]
    db.commit()
    db.close()
    return verify(user1, passwd)
