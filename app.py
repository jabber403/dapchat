import os
import json
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime

app = Flask(__name__)
# Secure secret key assignment for production serverless infrastructure
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dapchat_enterprise_crypto_key_2026')

# -------------------------------------------------------------------------
# ADVANCED SERVERLESS MEMORY STORAGE ENGINE & SCHEMAS
# -------------------------------------------------------------------------
# Because Vercel destroys local storage text files on sleep, we use an
# optimized global memory dictionary with lookup indexes for instant routing.
MEMORY_USERS = {
    "dapadmin": "admin123",
    "snapking": "snap123",
    "cyberghost": "ghost123"
}

MEMORY_CHATS = [
    {
        "room": "General",
        "text": "Welcome to the official launch of DapChat! 🚀",
        "image": "",
        "sender": "[Bot] System",
        "timestamp": "12:00 PM"
    },
    {
        "room": "Code-Talk",
        "text": "Flask engine optimized for Vercel Serverless Functions.",
        "image": "",
        "sender": "[Bot] Developer",
        "timestamp": "12:05 PM"
    }
]

MEMORY_DMS = []
MEMORY_STORIES = [
    {
        "username": "snapking",
        "image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100%' height='100%' fill='%23fffc00'/><text x='50%' y='55%' font-family='sans-serif' font-size='14' font-weight='bold' fill='black' text-anchor='middle'>LIVE NOW</text></svg>",
        "timestamp": "01:00 PM"
    }
]

# PERSISTENT STORAGE CAPABILITY FALLBACK FOR LOCAL MACHINES
DB_USERS = "db_users.txt"

def seed_database_from_local_disk():
    """ Scans local environments for existing user schemas to preserve state """
    global MEMORY_USERS
    try:
        if os.path.exists(DB_USERS):
            with open(DB_USERS, "r") as storage_file:
                for active_line in storage_file:
                    if active_line.strip():
                        parsed_record = json.loads(active_line.strip())
                        MEMORY_USERS[parsed_record['username']] = parsed_record['password']
    except Exception as cache_error:
        print(f"[Engine Warn] Disk synchronization bypassed: {cache_error}")

# Run sync check on startup
seed_database_from_local_disk()

# -------------------------------------------------------------------------
# MEMORY MONITORING & PURGE GARBAGE COLLECTION
# -------------------------------------------------------------------------
def optimize_memory_buffers():
    """ 
    Prevents serverless instance memory bloat from active Base64 image streams.
    Caps public channels and direct messaging histories at a strict length threshold.
    """
    global MEMORY_CHATS, MEMORY_DMS, MEMORY_STORIES
    MAX_BUFFER_CAPACITY = 100
    
    if len(MEMORY_CHATS) > MAX_BUFFER_CAPACITY:
        MEMORY_CHATS = MEMORY_CHATS[-MAX_BUFFER_CAPACITY:]
    if len(MEMORY_DMS) > MAX_BUFFER_CAPACITY:
        MEMORY_DMS = MEMORY_DMS[-MAX_BUFFER_CAPACITY:]
    if len(MEMORY_STORIES) > 20:
        MEMORY_STORIES = MEMORY_STORIES[-20:]

# -------------------------------------------------------------------------
# CORE APPLICATION ROUTING & CORE PAGES
# -------------------------------------------------------------------------

@app.route('/')
def index():
    """ Renders the primary workspace dashboard panel """
    if 'username' not in session:
        return redirect(url_for('login'))
    
    current_identity = session['username']
    
    # Filter out system entities and the requesting user from the direct message sidebar
    active_directory = [
        user_handle for user_handle in MEMORY_USERS.keys() 
        if user_handle != current_identity and not user_handle.startswith('[Bot]')
    ]
    
    preconfigured_rooms = {
        "General": {"is_private": False},
        "Gaming": {"is_private": False},
        "Code-Talk": {"is_private": False}
    }
    
    return render_template(
        'index.html', 
        username=current_identity, 
        rooms=preconfigured_rooms,
        users_list=active_directory,
        stories=MEMORY_STORIES[-10:]
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Manages user session authentication lookups """
    if request.method == 'POST':
        user_handle = request.form.get('username', '').strip()
        security_token = request.form.get('password', '')
        
        if not user_handle or not security_token:
            return "<h3>Missing credentials. <a href='/login'>Retry</a></h3>", 400
            
        if user_handle in MEMORY_USERS and MEMORY_USERS[user_handle] == security_token:
            session['username'] = user_handle
            return redirect(url_for('index'))
            
        return "<h3>Invalid identity configurations. <a href='/login'>Retry</a></h3>", 401
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """ Registers new credentials inside the memory matrix """
    if request.method == 'POST':
        user_handle = request.form.get('username', '').strip()
        security_token = request.form.get('password', '')
        
        # Rigorous input validation checks
        if not user_handle or not security_token:
            return "<h3>All fields are mandatory. <a href='/signup'>Back</a></h3>", 400
            
        if len(user_handle) < 3 or len(security_token) < 4:
            return "<h3>Credentials fail length regulations. <a href='/signup'>Back</a></h3>", 400
            
        if user_handle.startswith('[Bot]') or user_handle.lower() == 'system':
            return "<h3>Reserved handle naming pattern. <a href='/signup'>Back</a></h3>", 403
            
        if user_handle in MEMORY_USERS:
            return "<h3>Identity token already allocated. <a href='/signup'>Back</a></h3>", 409
            
        # Commit to real-time memory map
        MEMORY_USERS[user_handle] = security_token
        
        # Local system safety write fallback
        try:
            with open(DB_USERS, "a") as storage_append:
                storage_append.write(json.dumps({"username": user_handle, "password": security_token}) + "\n")
        except Exception:
            pass
            
        session['username'] = user_handle
        return redirect(url_for('index'))
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """ Destroys client browser cookie sessions """
    session.pop('username', None)
    return redirect(url_for('login'))

# -------------------------------------------------------------------------
# ASYNC PUBLIC CHANNEL MEDIA API WIRES
# -------------------------------------------------------------------------

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    """ Queries the network message stack for a specified room location """
    target_room = request.args.get('room')
    if not target_room:
        return jsonify({"error": "Missing parameter 'room'"}), 400
        
    isolated_history = [
        chat_packet for chat_packet in MEMORY_CHATS 
        if chat_packet.get('room') == target_room
    ]
    return jsonify(isolated_history[-35:])

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """ Appends an encoded public message packet into the cloud buffer """
    active_sender = session.get('username')
    if not active_sender:
        return jsonify({"error": "Session unauthenticated"}), 401
        
    payload_data = request.get_json() or {}
    target_room = payload_data.get('room')
    message_text = payload_data.get('text', '')
    media_packet = payload_data.get('image', '')
    
    if not target_room or (not message_text and not media_packet):
        return jsonify({"error": "Empty or malformed transmission structural data"}), 400
        
    compiled_chat_node = {
        'room': target_room,
        'text': message_text,
        'image': media_packet,
        'sender': active_sender,
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    MEMORY_CHATS.append(compiled_chat_node)
    optimize_memory_buffers()
    return jsonify({"status": "success", "scope": "channel"})

# -------------------------------------------------------------------------
# ASYNC DIRECT MESSAGING & STORIES ENGINE CORNERSTONES
# -------------------------------------------------------------------------

@app.route('/api/get_dms', methods=['GET'])
def get_dms():
    """ Fetches secure private communication channels for matching users """
    authenticated_identity = session.get('username')
    target_recipient = request.args.get('target')
    
    if not authenticated_identity or not target_recipient:
        return jsonify({"error": "Invalid channel parameters query context"}), 400
        
    # Generate bi-directional channel string hash sorting keys alphabetical
    shared_dm_hash_key = "-".join(sorted([authenticated_identity, target_recipient]))
    
    isolated_dm_history = [
        dm_packet for dm_packet in MEMORY_DMS 
        if dm_packet.get('dm_id') == shared_dm_hash_key
    ]
    return jsonify(isolated_dm_history[-35:])

@app.route('/api/send_dm', methods=['POST'])
def send_dm():
    """ Locks a private communication log node into memory """
    authenticated_identity = session.get('username')
    if not authenticated_identity:
        return jsonify({"error": "Session unauthenticated"}), 401
        
    payload_data = request.get_json() or {}
    target_recipient = payload_data.get('target')
    message_text = payload_data.get('text', '')
    media_packet = payload_data.get('image', '')
    
    if not target_recipient or (not message_text and not media_packet):
        return jsonify({"error": "Malformed network package specifications"}), 400
        
    shared_dm_hash_key = "-".join(sorted([authenticated_identity, target_recipient]))
    
    compiled_dm_node = {
        'dm_id': shared_dm_hash_key,
        'text': message_text,
        'image': media_packet,
        'sender': authenticated_identity,
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    MEMORY_DMS.append(compiled_dm_node)
    optimize_memory_buffers()
    return jsonify({"status": "success", "scope": "direct_message"})

@app.route('/api/upload_story', methods=['POST'])
def upload_story():
    """ Provisions a Base64 image string as a global snap status node """
    authenticated_identity = session.get('username')
    if not authenticated_identity:
        return jsonify({"error": "Session unauthenticated"}), 401
        
    payload_data = request.get_json() or {}
    base64_image_data = payload_data.get('image')
    
    if not base64_image_data:
        return jsonify({"error": "Empty visual array byte matrix allocation"}), 400
        
    compiled_story_node = {
        'username': authenticated_identity,
        'image': base64_image_data,
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    MEMORY_STORIES.append(compiled_story_node)
    optimize_memory_buffers()
    return jsonify({"status": "success", "scope": "stories_portal"})

# -------------------------------------------------------------------------
# SERVER CONTEXT INITIALIZATION RUNNERS
# -------------------------------------------------------------------------
if __name__ == '__main__':
    # Local diagnostic feedback log execution loop flags
    print("\n========================================================")
    print("      DAPCHAT CORE SERVICE NETWORK ENGINE STANDALONE    ")
    print("========================================================")
    print(" >>> Mode: High-Performance Network Polling Protocol Active")
    print(" >>> Address Allocation Target: http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=True)