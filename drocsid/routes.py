from flask import  url_for, redirect, render_template, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from drocsid.forms import RegisterForm, LoginForm
from drocsid import app,db,bcrypt
from drocsid.models import User

    
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ''
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        msg = "Account has been created"
        return redirect(url_for('login'))
    return render_template("register.html", form=form,msg= msg)

@app.route('/login', methods=["GET", "POST"])
def login():
    msg = ''
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            msg = "login successful"
            return redirect(url_for('main'))
        else:
            msg = "Login Unsuccessful. Check your username and password"
        
    return render_template('login.html', form=form, msg = msg)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/main')
@login_required
def main():
    return render_template('main.html')

@app.route('/chat', defaults={'room': None})
@app.route('/chat/<room>')
@login_required
def chat(room):
    print(room)
    return render_template('chat.html', username=current_user.username, room=room)
