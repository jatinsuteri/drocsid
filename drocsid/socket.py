from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from .extension import socketio, db
from drocsid.models import Message
from flask import redirect, url_for

connected_users = {}

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        print(f"{current_user.username} connected.")

@socketio.on('user_join')
def handle_user_join(data):
    username = data['username']
    room = data['room'] 
    join_room(room)
    if room not in connected_users:
        connected_users[room] = []
    if username not in connected_users[room]:
        connected_users[room].append(username)
    emit("user_joined", {"users": connected_users[room]}, room=room)  
    print(f"{username} has joined room: {room}")

@socketio.on('new_message')
def handle_new_message(data):
    room = data['room'] 
    message = data['message']
    currentuser = current_user.username
    print(f"New message from {current_user.username} in {room}: {message}")
    new_message = Message(room=room, username=currentuser, user_id=current_user.id, message=message)
    db.session.add(new_message)
    db.session.commit()
    emit("chat", {"message": message, "username": current_user.username}, to=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    username = data['username']
    leave_room(room)

    if room in connected_users and username in connected_users[room]:
        connected_users[room].remove(username)

    emit('user_left', {'users': connected_users.get(room, [])}, room=room)  
    print(f"{username} has left room: {room}")

@socketio.on('disconnect')
def handle_disconnect():
    username = current_user.username
    for room, users in connected_users.items():
        if username in users:
            users.remove(username)
            emit('user_left', {'users': users}, room=room)
            print(f"{username} has disconnected from room: {room}")