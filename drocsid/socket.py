from flask_socketio import emit, join_room, leave_room, send
from flask_login import current_user
from .extension import socketio

@socketio.on('connect')
def handle_connect():
    print(f"{current_user.username} connected.")

@socketio.on('user_join')
def handle_user_join(data):
    username = data['username']
    room = data['room'] 
    join_room(room)
    send(f"{username} has joined the chat.", to=room)
    print(f"{username} has joined room: {room}")

@socketio.on('new_message')
def handle_new_message(data):
    room = data['room'] 
    message = data['message']
    print(f"new message from {current_user.username} in {room}: {message}")
    emit("chat", {"message": message, "username": current_user.username}, to=room)
