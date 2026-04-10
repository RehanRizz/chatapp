from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from functools import wraps
import config

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
socketio = SocketIO(app)

WHITELIST = config.WHITELIST
ENTRY_PASSWORD = config.ENTRY_PASSWORD

connected_users = {}


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/", methods=["GET"])
def index():
    if "username" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if username not in WHITELIST:
            error = "This username is not allowed."
        elif password != ENTRY_PASSWORD:
            error = "Incorrect password."
        else:
            session["username"] = username
            return redirect(url_for("chat"))

    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html", username=session["username"])


# Socket.IO events
@socketio.on("connect")
def handle_connect():
    username = session.get("username")

    if not username or username not in WHITELIST:
        return False  # reject connection

    connected_users[request.sid] = username
    emit("system_message", {"msg": f"{username} joined the chat."}, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    username = connected_users.pop(request.sid, None)
    if username:
        emit("system_message", {"msg": f"{username} left the chat."}, broadcast=True)


@socketio.on("chat_message")
def handle_chat_message(data):
    username = connected_users.get(request.sid, "Unknown")
    msg = data.get("msg", "")
    if msg.strip():
        emit("chat_message", {"user": username, "msg": msg}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5050, debug=True)