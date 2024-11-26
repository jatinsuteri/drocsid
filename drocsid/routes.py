from flask import  url_for, redirect, render_template, flash, request,jsonify
from flask_login import current_user, login_user, logout_user, login_required
from drocsid.forms import RegisterForm, LoginForm
from drocsid import app,bcrypt
from .extension import db
from drocsid.models import User,Message,Friendship,FriendRequest

    
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

@app.route('/main', methods=["GET", "POST"])
@login_required
def main():
    if request.method == "POST":
        friend = request.form.get('user-search')
        user = User.query.filter_by(username=friend).first()
        if user:
            func(user)
        else:
            flash('User not found.')
        return redirect(url_for('main')) 

    return render_template('main.html')

#route to display list of friends for the js in the main file
#will retrn the list of friends in json format
@app.route('/api/get_friends', methods=["GET"])
@login_required
def get_friends():
    user_id = current_user.id
    friends = db.session.query(User).join(
        Friendship,
        (Friendship.user1_id == user_id) & (Friendship.user2_id == User.id) |
        (Friendship.user2_id == user_id) & (Friendship.user1_id == User.id)
    ).all()

    friends_data = [
        {"id": friend.id, "username": friend.username, "profile_picture": None} 
        for friend in friends
    ]

    return jsonify({"friends": friends_data})

#static rooms routes

@app.route('/chat/<room>', methods=["GET", "POST"])
@login_required
def chat(room):
    messages = Message.query.filter_by(room=room).order_by(Message.timestamp.asc()).all()
    return render_template('chat.html', username=current_user.username, room=room, messages=messages)


# @app.route('/check_user', methods=['POST'])
# @login_required
# def check_user():
#     data = request.json
#     username = data.get('username')
#     user = User.query.filter_by(username=username).first()
#     return jsonify({'valid': user is not None and user != current_user})

# @app.route('/chat/<room>', methods=["GET", "POST"])
# @login_required
# def chat(room):
#     if room.startswith('dm_'):
#         dm_username = room[3:]
#         dm_user = User.query.filter_by(username=dm_username).first()
#         if not dm_user:
#             flash('Invalid username for DM.')
#             return redirect(url_for('main'))
#         messages = Message.query.filter(
#             ((Message.user_id == current_user.id) & (Message.receiver_id == dm_user.id) & Message.is_dm) |
#             ((Message.user_id == dm_user.id) & (Message.receiver_id == current_user.id) & Message.is_dm)
#         ).order_by(Message.timestamp.asc()).all()
#     else:
#         messages = Message.query.filter_by(room=room, is_dm=False).order_by(Message.timestamp.asc()).all()
    
#     return render_template('chat.html', username=current_user.username, room=room, messages=messages)

# #################################### ##

#testing friendship system

# non routes functions 
def func(user):
    if user == current_user:
        flash('You cannot add yourself as a friend.')
    elif Friendship.query.filter_by(user1_id=current_user.id, user2_id=user.id).first():
        flash(f'You are already friends with {user.username}.')
    elif FriendRequest.query.filter_by(sender_id=current_user.id, receiver_id=user.id).first():
        flash(f'A friend request has already been sent to {user.username}.')
    elif FriendRequest.query.filter_by(sender_id=user.id, receiver_id=current_user.id).first():
        flash(f'You have already received a friend request from {user.username}.')
    else:
        friend_request = FriendRequest(sender_id=current_user.id, receiver_id=user.id)
        db.session.add(friend_request)
        db.session.commit()
        flash(f'Friend request sent to {user.username}.')