from flask import Flask, render_template, request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import  datetime
import json
from flask_mail import Mail,Message
import os
from werkzeug.utils import secure_filename
import math
import mysql.connector

with open('config.json','r') as c :
    params = json.load(c)["params"]


app = Flask(__name__)
app.secret_key = 'super-secret-key'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = params['gmail-user']
app.config['MAIL_PASSWORD'] = params['gmail-password']
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/csv_db 8'

mail = Mail(app)

db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    book = db.Column(db.String(100), unique=False, nullable=False)
    author = db.Column(db.String(100), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)

class Books(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    author = db.Column(db.String(100), unique=False, nullable=False)

class Contacts(db.Model):
    '''srno, name, email, phone, message , date'''
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=False, nullable=False)
    phone = db.Column(db.String(10), unique=False, nullable=False)
    messege = db.Column(db.String(100), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False,nullable=True)


@app.route("/", methods=['GET', 'POST'])
def index():
    if (request.method == 'POST'):
        '''add entry to data base'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')

        entry = Contacts(name=name, email=email, phone=phone, date=datetime.now(), messege=msg)
        db.session.add(entry)
        db.session.commit()
        e_msg = Message("new message from " + name,
                        sender=email,
                        recipients=[params['gmail-user']],
                        body=msg + "\n" + phone)

        mail.send(e_msg)
    return render_template('index.html')

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_username']):
        member = Member.query.all()
        return render_template('dashboard.html', member = member)

    if request.method == "POST":
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if (username == params['admin_username'] and userpass == params['admin_password']):
            # set the session variable
            session['user'] = username
            member = Member.query.all()
            return render_template('dashboard.html', member=member)
    return render_template("login.html")

@app.route("/edit/<string:id>" ,methods=['GET','POST'])
def edit(id):
    if ('user' in session and session['user'] == params['admin_username']) :
        if request.method == "POST" :
            name = request.form.get('name')
            book = request.form.get('book')
            author = request.form.get('author')
            date = datetime.now()
            if id == '0':
                member = Member(name=name, book=book, author=author, date=date)
                db.session.add(member)
                db.session.commit()
            else:
                member = Member.query.filter_by(id = id).first()
                # post.id = id
                member.name = name
                member.book = book
                member.author = author
                member.date = date
                db.session.commit()
                return redirect('/edit/'+id)
        member = Member.query.filter_by(id=id).first()
        return render_template("edit.html",params=params,member=member,id=id)



@app.route("/delete/<string:id>" ,methods=['GET','POST'])
def Delete(id) :
    if ('user' in session and session['user'] == params['admin_username']):
        member = Member.query.filter_by(id = id).first()
        db.session.delete(member)
        db.session.commit()
        return redirect("/dashboard")


@app.route("/search", methods = ['GET', 'POST'])
def search():
    if ('user' in session and session['user'] == params['admin_username']):
        a = ""
        t = ""
        if (request.method == "POST"):
            search = request.form.get('search')
            books = Books.query.all()
            for book in books:
                if(book.title == search):
                    a = book.author
                    t = book.title
        return render_template("search.html",a=a, t=t)


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


app.run(debug=True)
