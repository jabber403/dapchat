import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime

app = Flask(__name__)

# SECURITY PRODUCTION FIX: Pulls the key safely from Render's Environment Variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'local_development_fallback_key_123')

# Using standard WebSockets without heavy database extension requirements
socketio = SocketIO(app, cors_allowed_origins="*")

# --- IN-MEMORY DATABASE (Pure Python) ---
USERS = {}          # Format: { "username": "password" }
STORIES = []        # Format: [ {"username": "...", "content": "...", "time": "..."} ]
CHAT_HISTORY = {    # Stores persistent messages per room
    "General": [],
    "Gaming": [],
    "Code-Talk": []
}

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'], stories=STORIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        
        return "<h3>Invalid Username or Password. <a href='/login'>Try again</a></h3>"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        
        if not username or not password:
            return "<h3>Fields cannot be empty! <a href='/signup'>Try again</a></h3>"
        
        if username in USERS:
            return "<h3>Username already taken! <a href='/signup'>Try again</a></h3>"
        
        USERS[username] = password
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/create-story', methods=['POST'])
def create_story():
    if 'username' in session:
        content = request.form.get('story_content')
        if content:
            STORIES.append({
                'username': session['username'],
                'content': content,
                'time': datetime.now().strftime('%I:%M %p')
            })
    return redirect(url_for('index'))

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('room_history', CHAT_HISTORY.get(room, []))

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    msg_data = {
        'text': data['text'],
        'sender': session.get('username', 'Anonymous')
    }
    if room in CHAT_HISTORY:
        CHAT_HISTORY[room].append(msg_data)
        
    emit('receive_message', msg_data, to=room)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)