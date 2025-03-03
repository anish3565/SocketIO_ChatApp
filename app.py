from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary storing connected users (Key: socketid, Value: avatar URL & username)
users = {}

@app.route('/')
def index():
    return render_template('index.html')

# When a new user connects
@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000,9999)}"
    gender = random.choice(["girl", "boy"])
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={username}"

    users[request.sid] = {"username": username, "avatar": avatar_url}

    emit("user_joined", {"username": username, "avatar": avatar_url}, broadcast=True)
    emit("set_username", {"username": username, "avatar": avatar_url})

# When a user disconnects
@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)

# Handle sending messages
@socketio.on("send_message")
def handle_send_message(data):
    user = users.get(request.sid)
    if user:
        emit("new_message", {
            "username": user["username"],
            "avatar": user["avatar"],
            "message": data["message"]
        }, broadcast=True)

# Handle username updates
@socketio.on("update_username")
def handle_update_username(data):
    old_username = users[request.sid]["username"]
    new_username = data["new_username"]
    gender = data["gender"]
    
    # Generate new avatar URL based on the selected gender
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={new_username}"
    
    # Update both username and avatar
    users[request.sid]["username"] = new_username
    users[request.sid]["avatar"] = avatar_url

    emit("username_updated", {
        "old_username": old_username,
        "new_username": new_username,
        "avatar": avatar_url
    }, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)