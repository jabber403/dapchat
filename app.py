import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

app = Flask(__name__)

# PRODUCTION SECURITY: Uses a robust variable on Render with a local backup string
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'aero_secure_fallback_platform_key_2026')

# Initialize SocketIO with cross-origin parameters for flexible connectivity
socketio = SocketIO(app, cors_allowed_origins="*")

# --- CENTRAL STORAGE SYSTEM (In-Memory Engine) ---
USERS = {}          # Database Schema: { "username": "password" }
BOTS = {}          # Database Schema: { "bot_token": { "name": "...", "creator": "..." } }
STORIES = []        # Global list of temporary user stories

# Complete Workspace Chat System
GROUP_CHATS = {
    "General": {"is_private": False, "allowed_members": [], "history": []},
    "Gaming": {"is_private": False, "allowed_members": [], "history": []},
    "Code-Talk": {"is_private": False, "allowed_members": [], "history": []}
}

# Private Direct Messages Registry (Keys generated dynamically as "user1-user2")
PRIVATE_DMS = {}

# --- CORE USER WEB INTERFACES ---

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    # Build list of user profiles to choose from for Private DMs
    available_users = [u for u in USERS.keys() if u != session['username'] and not u.endswith('_bot')]
    
    return render_template(
        'index.html', 
        username=session['username'], 
        stories=STORIES,
        rooms=GROUP_CHATS,
        users_list=available_users,
        bots_list=[b['name'] for b in BOTS.values() if b['creator'] == session['username']]
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
            
        return "<h3>Authentication Failed. <a href='/login'>Try Again</a></h3>"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        if not username or not password:
            return "<h3>Fields cannot be empty. <a href='/signup'>Try Again</a></h3>"
        if username in USERS or username.endswith('_bot'):
            return "<h3>Username unavailable or reserved. <a href='/signup'>Try Again</a></h3>"
            
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
        content = request.form.get('story_content', '').strip()
        if content:
            STORIES.append({
                'username': session['username'],
                'content': content,
                'time': datetime.now().strftime('%I:%M %p')
            })
    return redirect(url_for('index'))

# --- PRIVATE GROUPS SYSTEM ---

@app.route('/create-private-group', methods=['POST'])
def create_private_group():
    creator = session.get('username')
    if not creator: return redirect(url_for('login'))
    
    group_name = request.form.get('group_name', '').strip().replace(" ", "-")
    if group_name and group_name not in GROUP_CHATS:
        GROUP_CHATS[group_name] = {
            "is_private": True,
            "allowed_members": [creator],
            "history": []
        }
    return redirect(url_for('index'))

# --- DEVELOPER BOTFATHER API ENGINE ---

@app.route('/botfather/create', methods=['POST'])
def create_bot():
    creator = session.get('username')
    if not creator:
        return jsonify({"error": "Unauthorized session"}), 401
        
    bot_name = request.form.get('bot_name', '').strip()
    if not bot_name.endswith('_bot') or " " in bot_name:
        return jsonify({"error": "Bot username must look like: sample_bot"}), 400
    if bot_name in USERS:
        return jsonify({"error": "Bot username is already registered"}), 400

    # Mint a secure application programming token
    bot_token = f"aero-{uuid.uuid4().hex[:14]}"
    
    BOTS[bot_token] = {
        "name": bot_name,
        "creator": creator
    }
    
    # Establish bot instance inside routing permissions
    USERS[bot_name] = "APP_BOT_PROTECTED_PASSWORD_SYSTEM"
    
    return jsonify({
        "status": "success",
        "bot_username": f"@{bot_name}",
        "access_token": bot_token,
        "endpoint": f"/api/bot/{bot_token}/sendMessage"
    })

@app.route('/api/bot/<token>/sendMessage', methods=['POST'])
def bot_api_gateway(token):
    if token not in BOTS:
        return jsonify({"error": "Access token unrecognized"}), 403
        
    bot_profile = BOTS[token]
    payload = request.get_json() or request.form
    
    target_chat = payload.get('chat_id')
    text_content = payload.get('text')
    
    if not target_chat or not text_content:
        return jsonify({"error": "Parameters missing: chat_id and text required"}), 400
        
    if target_chat not in GROUP_CHATS:
        return jsonify({"error": "Target channel layout not found"}), 404

    message_packet = {
        'text': text_content,
        'sender': bot_profile['name'],
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    # Pipeline the message straight into the workspace chat
    GROUP_CHATS[target_chat]['history'].append(message_packet)
    socketio.emit('receive_message', {
        'room': target_chat,
        'msg': message_packet
    }, to=target_chat)
    
    return jsonify({"delivery": "fulfilled", "origin": bot_profile['name']}), 200

# --- WEBSOCKET REAL-TIME ARCHITECTURE ---

@socketio.on('join_room')
def handle_room_joining(data):
    user = session.get('username')
    room = data.get('room')
    if not user or not room: return
    
    # Enforce strict verification rules for invite-only networks
    if room in GROUP_CHATS and GROUP_CHATS[room]['is_private']:
        if user not in GROUP_CHATS[room]['allowed_members']:
            emit('error_alert', {'msg': 'Access Denied: Private Group Chat'})
            return
            
    join_room(room)
    emit('sync_history', GROUP_CHATS.get(room, {}).get('history', []))

@socketio.on('send_group_msg')
def handle_group_distribution(data):
    user = session.get('username')
    room = data.get('room')
    text = data.get('text')
    if not user or not room or not text: return
    
    message_packet = {
        'text': text,
        'sender': user,
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    if room in GROUP_CHATS:
        GROUP_CHATS[room]['history'].append(message_packet)
        emit('receive_message', {'room': room, 'msg': message_packet}, to=room)

@socketio.on('join_private_dm')
def handle_dm_joining(data):
    me = session.get('username')
    target = data.get('target')
    if not me or not target: return
    
    # Build unique sorting key for private room identification
    dm_channel_id = "-".join(sorted([me, target]))
    join_room(dm_channel_id)
    
    if dm_channel_id not in PRIVATE_DMS:
        PRIVATE_DMS[dm_channel_id] = []
        
    emit('sync_dm_history', PRIVATE_DMS[dm_channel_id])

@socketio.on('send_private_dm')
def handle_dm_distribution(data):
    me = session.get('username')
    target = data.get('target')
    text = data.get('text')
    if not me or not target or not text: return
    
    dm_channel_id = "-".join(sorted([me, target]))
    message_packet = {
        'text': text,
        'sender': me,
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    if dm_channel_id not in PRIVATE_DMS:
        PRIVATE_DMS[dm_channel_id] = []
        
    PRIVATE_DMS[dm_channel_id].append(message_packet)
    emit('receive_private_dm', message_packet, to=dm_channel_id)

if __name__ == '__main__':
    assigned_port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=assigned_port)