import hashlib, os, binascii, sqlite3
#type is the group(class - 2C or teacher or class's main teacher - classteacher2C)


def hash(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

print("Welcome to smarTest!")
print("Your login is: admin")
passwd=input("Insert password: ")
while(passwd==""):
    passwd=input("No password inserted! Insert password: ")
name=input("Input your full name: ")
mail=input("Input your e-mail address: ")
teachers=input("Please the password for teacher signup: ")
print("Please remember this password because without it teachers are not able to signup!")

db = sqlite3.connect("smartest.db")
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS tests(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT,desc TEXT,start_date TEXT,end_date TEXT,time TEXT,teacher TEXT, type TEXT, maxpoints TEXT, checked TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS teacher_cred(hash TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS users(name TEXT UNIQUE,password TEXT,full_name TEXT,mail TEXT,type TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS messages(sender TEXT,recipient TEXT,date TEXT,time TEXT,read TEXT, header TEXT, content TEXT)''')
cursor.execute('''INSERT INTO users(name,password,full_name,mail,type) VALUES(?,?,?,?,?)''', ("admin",hash(passwd),name,mail,"admin"))
cursor.execute('''INSERT INTO teacher_cred(hash) VALUES(?)''', ((hash(teachers),)))
db.commit()
db.close()
