# server.py
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

# Dictionary to store peer connections
pcs = {}

@sio.event
async def connect(sid, environ):
    print(f'User {sid} connected')

@sio.event
async def disconnect(sid):
    print(f'User {sid} disconnected')
    if sid in pcs:
        pc = pcs[sid]
        await pc.close()
        del pcs[sid]

@sio.event
async def offer(sid, data):
    pc = RTCPeerConnection()
    pcs[sid] = pc

    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate:
            await sio.emit("icecandidate", {"candidate": candidate}, to=sid)

    # Set the remote description (the offer from the peer)
    await pc.setRemoteDescription(RTCSessionDescription(data['sdp'], data['type']))

    # Create an answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Send the answer back to the peer
    await sio.emit("answer", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}, to=sid)

@sio.event
async def icecandidate(sid, data):
    candidate = data.get("candidate")
    if candidate:
        await pcs[sid].addIceCandidate(candidate)
