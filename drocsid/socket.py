from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from .extension import socketio, db
from drocsid.models import Message
from drocsid.models import User

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
    
    if room.startswith('dm_'):
        dm_username = room[3:]
        dm_user = User.query.filter_by(username=dm_username).first()
        if dm_user:
            new_message = Message(
                user_id=current_user.id,
                recipient_id=dm_user.id,
                username=currentuser,
                message=message
            )
            db.session.add(new_message)
            db.session.commit()
            emit("chat", {"message": message, "username": currentuser}, to=room)
    else:
        new_message = Message(room=room, username=currentuser, user_id=current_user.id, message=message)
        db.session.add(new_message)
        db.session.commit()
        emit("chat", {"message": message, "username": currentuser}, to=room)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    if room not in connected_users:
        connected_users[room] = set()
    connected_users[room].add(username)
    emit('user_joined', {'user': username, 'users': list(connected_users[room])}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    if room in connected_users and username in connected_users[room]:
        connected_users[room].remove(username)
        emit('user_left', {'user': username, 'users': list(connected_users[room])}, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    username = current_user.username
    for room, users in connected_users.items():
        if username in users:
            users.remove(username)
            emit('user_left', {'users': users}, room=room)
            print(f"{username} has disconnected from room: {room}")