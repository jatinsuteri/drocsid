from flask_socketio import emit, join_room, leave_room, send
from flask_login import current_user
from .extension import socketio,db
from drocsid.models import Message


@socketio.on('connect')
def handle_connect():
    print(f"{current_user.username} connected.")

@socketio.on('user_join')
def handle_user_join(data):
    username = data['username']
    room = data['room'] 
    join_room(room)
    emit("join",{"username" : current_user.username}, to=room)
    print(f"{username} has joined room: {room}")

@socketio.on('new_message')
def handle_new_message(data):
    room = data['room'] 
    message = data['message']
    currentuser = current_user.username
    print(f"new message from {current_user.username} in {room}: {message}")
    new_message = Message(room=room, username = currentuser, user_id = currentuser, message=message)
    db.session.add(new_message)
    db.session.commit()
    emit("chat", {"message": message, "username": current_user.username}, to=room)
