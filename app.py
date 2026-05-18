import os
import json
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'aero_flatfile_db_2026')

# --- CUSTOM FLAT-FILE DATABASE CORE ENGINE ---
# This forces data onto the disk immediately, keeping RAM close to 0MB.
DB_USERS = "db_users.txt"
DB_KEYS = "db_keys.txt"
DB_CHATS = "db_chats.txt"
DB_DMS = "db_dms.txt"

def init_db():
    """ Ensures all flat-file database tables exist on boot """
    for db_file in [DB_USERS, DB_KEYS, DB_CHATS, DB_DMS]:
        if not os.path.exists(db_file):
            with open(db_file, "w") as f:
                f.write("")

init_db()

def read_rows(file_path):
    """ Custom database row scanner """
    rows = []
    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line.strip()))
    return rows

def append_row(file_path, data):
    """ Custom database row writer """
    with open(file_path, "a") as f:
        f.write(json.dumps(data) + "\n")

# --- APP INTERFACES & AUTHENTICATION SYSTEMS ---

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    current_user = session['username']
    all_users = [row['username'] for row in read_rows(DB_USERS)]
    available_users = [u for u in all_users if u != current_user and not u.startswith('[Bot]')]
    
    # Filter keys belonging to this developer
    all_keys = read_rows(DB_KEYS)
    user_keys = [row['api_key'] for row in all_keys if row['developer'] == current_user]
    
    # Unique system room structures
    rooms = {
        "General": {"is_private": False},
        "Gaming": {"is_private": False},
        "Code-Talk": {"is_private": False}
    }
    
    return render_template(
        'index.html', 
        username=current_user, 
        rooms=rooms,
        users_list=available_users,
        developer_keys=user_keys
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        for row in read_rows(DB_USERS):
            if row['username'] == username and row['password'] == password:
                session['username'] = username
                return redirect(url_for('index'))
        return "<h3>Login Failed. <a href='/login'>Try Again</a></h3>"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        if not username or not password or username.startswith('[Bot]'):
            return "<h3>Invalid input choices. <a href='/signup'>Try Again</a></h3>"
            
        # Check duplicate records
        for row in read_rows(DB_USERS):
            if row['username'] == username:
                return "<h3>Username Taken. <a href='/signup'>Try Again</a></h3>"
                
        append_row(DB_USERS, {"username": username, "password": password})
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# --- CUSTOM STORAGE SYNCHRONIZATION API ---

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    room = request.args.get('room')
    all_chats = read_rows(DB_CHATS)
    # Filter database entries matching this specific room name
    room_history = [msg for msg in all_chats if msg.get('room') == room]
    return jsonify(room_history[-15:]) # Limit payload sizes to keep execution clean

@app.route('/api/send_message', methods=['POST'])
def send_message():
    user = session.get('username')
    data = request.get_json() or {}
    room = data.get('room')
    text = data.get('text')
    
    if user and room and text:
        msg_record = {
            'room': room,
            'text': text,
            'sender': user,
            'timestamp': datetime.now().strftime('%I:%M %p')
        }
        append_row(DB_CHATS, msg_record)
        return jsonify({"status": "success"})
    return jsonify({"error": "malformed_packet"}), 400

@app.route('/api/get_dms', methods=['GET'])
def get_dms():
    me = session.get('username')
    target = request.args.get('target')
    if not me or not target: return jsonify([])
    
    dm_id = "-".join(sorted([me, target]))
    all_dms = read_rows(DB_DMS)
    dm_history = [msg for msg in all_dms if msg.get('dm_id') == dm_id]
    return jsonify(dm_history[-15:])

@app.route('/api/send_dm', methods=['POST'])
def send_dm():
    me = session.get('username')
    data = request.get_json() or {}
    target = data.get('target')
    text = data.get('text')
    
    if me and target and text:
        dm_id = "-".join(sorted([me, target]))
        dm_record = {
            'dm_id': dm_id,
            'text': text,
            'sender': me,
            'timestamp': datetime.now().strftime('%I:%M %p')
        }
        append_row(DB_DMS, dm_record)
        return jsonify({"status": "success"})
    return jsonify({"error": "malformed_packet"}), 400

# --- PROPRIETARY AERO DEVELOPER API PORTAL ---

@app.route('/developer/keygen', methods=['POST'])
def generate_developer_key():
    developer = session.get('username')
    if not developer: return jsonify({"error": "unauthorized"}), 401
    app_name = request.form.get('app_name', '').strip()
    if not app_name: return jsonify({"error": "app_name_required"}), 400
    
    api_key = f"aero_live_{secrets.token_hex(12)}"
    append_row(DB_KEYS, {"api_key": api_key, "developer": developer, "app_name": app_name})
    return jsonify({"status": "minted", "api_key": api_key, "app_name": app_name})

@app.route('/aero-api/v1/broadcast', methods=['POST'])
def aero_custom_api_broadcast():
    payload = request.get_json() or {}
    api_key = payload.get('aero_key')
    target_channel = payload.get('channel')
    message_body = payload.get('message')
    bot_identity = payload.get('sender_identity', 'AeroBot')

    # Validate key from database rows
    key_valid = False
    app_source = "Unknown"
    for row in read_rows(DB_KEYS):
        if row['api_key'] == api_key:
            key_valid = True
            app_source = row['app_name']
            break
            
    if not key_valid: return jsonify({"api_error": "Invalid aero_key"}), 403
    if not target_channel or not message_body: return jsonify({"api_error": "Missing parameters"}), 400

    transmission = {
        'room': target_channel,
        'text': message_body,
        'sender': f"[Bot] {bot_identity}",
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    append_row(DB_CHATS, transmission)
    return jsonify({"aero_status": "dispatched", "origin_app": app_source, "destination": target_channel}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))