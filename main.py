import os, os.path, random, hashlib, sys, json
from flask import Flask, flash, render_template, redirect, request, url_for, jsonify, session, Response
from login import signup_f, login_f
from functions import *

app = Flask(__name__)
app.secret_key = '9je0jaj09jk9dkakdwjnjq'

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
            return render_template('teacher.html', username = session.get('username'))
        else:
            return render_template('student.html', username = session.get('username'))
    else:
        return redirect(url_for('login'))

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
        	#zły login lub hasło
            return render_template('signup.html')
    return render_template('signup.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['username']
    del session['password']
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)
