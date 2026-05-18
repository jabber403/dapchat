import os
import json
import secrets
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime

# -------------------------------------------------------------------------
# INITIALIZATION & LOGGING CONFIGURATION
# -------------------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dapchat_ultra_quantum_crypto_key_2026')

# Initialize developer telemetry logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DapChatCore")

# -------------------------------------------------------------------------
# GLOBAL SERVERLESS DATA MEMORY MATRIX
# -------------------------------------------------------------------------
# Vercel resets file configurations on sleep cycles. This optimized structure
# utilizes lookups, state logs, and automated bot simulations.
MEMORY_USERS = {
    "dapadmin": "admin123",
    "snapking": "snap123",
    "cyberghost": "ghost123",
    "pixelwarrior": "pixel456"
}

MEMORY_CHATS = [
    {
        "room": "General",
        "text": "Welcome to the premium serverless matrix of DapChat! 🚀",
        "image": "",
        "sender": "[Bot] System",
        "timestamp": "12:00 PM"
    },
    {
        "room": "General",
        "text": "Voice and Video streams are fully operational. Click any user profile to call.",
        "image": "",
        "sender": "[Bot] Aero",
        "timestamp": "12:01 PM"
    },
    {
        "room": "Code-Talk",
        "text": "Engine architecture updated: Python 3.10+ / Flask Micro-routing.",
        "image": "",
        "sender": "[Bot] Matrix",
        "timestamp": "12:05 PM"
    }
]

MEMORY_DMS = []
MEMORY_STORIES = [
    {
        "username": "cyberghost",
        "image": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'><rect width='100%' height='100%' fill='%23007aff'/><text x='50%' y='55%' font-family='sans-serif' font-size='12' fill='white' text-anchor='middle'>ONLINE</text></svg>",
        "timestamp": "11:30 AM"
    }
]

# WebRTC Signaling routing arrays
ACTIVE_SIGNALS = {}
CALL_HISTORY_LOGS = []

DB_USERS = "db_users.txt"

# -------------------------------------------------------------------------
# SECURITY ENGINE & TEXT SANITIZATION
# -------------------------------------------------------------------------
def sanitize_user_input(dirty_string):
    """
    Prevents Cross-Site Scripting (XSS) attacks by removing hazardous HTML tags
    before rendering input into client browser templates.
    """
    if not dirty_string:
        return ""
    clean_string = dirty_string.replace("<", "&lt;").replace(">", "&gt;")
    clean_string = clean_string.replace("script", "[blocked]")
    return clean_string.strip()

# -------------------------------------------------------------------------
# MEMORY RETENTION & GARBAGE COLLECTION MANAGER
# -------------------------------------------------------------------------
def run_garbage_collection_sweep():
    """
    Prevents serverless functions from exceeding strict internal RAM thresholds
    by purging old chat history indexes and caching payloads safely.
    """
    global MEMORY_CHATS, MEMORY_DMS, MEMORY_STORIES, CALL_HISTORY_LOGS
    CAPACITY_CEILING = 150
    
    try:
        if len(MEMORY_CHATS) > CAPACITY_CEILING:
            MEMORY_CHATS = MEMORY_CHATS[-CAPACITY_CEILING:]
            logger.info("[GC] Global public channels memory buffer truncated.")
            
        if len(MEMORY_DMS) > CAPACITY_CEILING:
            MEMORY_DMS = MEMORY_DMS[-CAPACITY_CEILING:]
            logger.info("[GC] Secure private messaging logs truncated.")
            
        if len(MEMORY_STORIES) > 25:
            MEMORY_STORIES = MEMORY_STORIES[-25:]
            
        if len(CALL_HISTORY_LOGS) > 50:
            CALL_HISTORY_LOGS = CALL_HISTORY_LOGS[-50:]
    except Exception as ec:
        logger.error(f"[GC Error] Automated memory purge failure: {ec}")

# -------------------------------------------------------------------------
# AUTHENTICATION FRAMEWORK & ROUTING ARCHITECTURE
# -------------------------------------------------------------------------
@app.route('/')
def index():
    """ Renders the active application frame controller workspace """
    if 'username' not in session:
        return redirect(url_for('login'))
    
    current_identity = session['username']
    
    # Filter directories to hide self identity and running system bots
    user_directory = [
        profile_handle for profile_handle in MEMORY_USERS.keys()
        if profile_handle != current_identity and not profile_handle.startswith('[Bot]')
    ]
    
    available_rooms = {
        "General": {"desc": "Main Hub Communication Array"},
        "Gaming": {"desc": "Multimedia Lounge Grid"},
        "Code-Talk": {"desc": "Systems Development Frameworks"}
    }
    
    return render_template(
        'index.html',
        username=current_identity,
        rooms=available_rooms,
        users_list=user_directory,
        stories=MEMORY_STORIES[-12:]
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Validates login credentials and initialises token session contexts """
    if request.method == 'POST':
        user_handle = request.form.get('username', '').strip()
        security_token = request.form.get('password', '')
        
        if not user_handle or not security_token:
            return "<h3>Credential verification packets missing fields. <a href='/login'>Retry</a></h3>", 400
            
        if user_handle in MEMORY_USERS and MEMORY_USERS[user_handle] == security_token:
            session['username'] = user_handle
            logger.info(f"[Auth] User @{user_handle} verified security key matches.")
            return redirect(url_for('index'))
            
        return "<h3>Authentication mismatch signature. <a href='/login'>Retry</a></h3>", 401
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """ Registers new credentials inside the memory matrix schemas """
    if request.method == 'POST':
        user_handle = request.form.get('username', '').strip()
        security_token = request.form.get('password', '')
        
        if not user_handle or not security_token:
            return "<h3>All configuration fields must be provided. <a href='/signup'>Back</a></h3>", 400
            
        if len(user_handle) < 3 or len(security_token) < 4:
            return "<h3>Input does not comply with structural guidelines. <a href='/signup'>Back</a></h3>", 400
            
        if user_handle.startswith('[Bot]') or user_handle.lower() == 'system':
            return "<h3>Reserved identification prefix detected. <a href='/signup'>Back</a></h3>", 403
            
        if user_handle in MEMORY_USERS:
            return "<h3>Identity footprint already verified in active map. <a href='/signup'>Back</a></h3>", 409
            
        # Write directly to allocation data grid
        MEMORY_USERS[user_handle] = security_token
        
        # Local system safety write logging fallback
        try:
            with open(DB_USERS, "a") as disk_append:
                disk_append.write(json.dumps({"username": user_handle, "password": security_token}) + "\n")
        except Exception:
            pass
            
        session['username'] = user_handle
        logger.info(f"[System] Minted new user profile signature for @{user_handle}")
        return redirect(url_for('index'))
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """ Clears secure authentication browser session structures """
    user_handle = session.get('username', 'Unknown')
    session.pop('username', None)
    logger.info(f"[Auth] User @{user_handle} terminated session routing successfully.")
    return redirect(url_for('login'))

# -------------------------------------------------------------------------
# CORE CHAT COMMUNICATIONS & FILE TRANSMISSION ENDPOINTS
# -------------------------------------------------------------------------
@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    """ Queries active chat buffers matching explicit room locations """
    target_channel = request.args.get('room')
    if not target_channel:
        return jsonify({"error": "Null parameter 'room'"}), 400
        
    channel_history = [
        packet for packet in MEMORY_CHATS
        if packet.get('room') == target_channel
    ]
    return jsonify(channel_history[-40:])

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """ Appends verified structural messages to active public streams """
    active_identity = session.get('username')
    if not active_identity:
        return jsonify({"error": "Session verification denied"}), 401
        
    packet_payload = request.get_json() or {}
    target_channel = packet_payload.get('room')
    message_content = sanitize_user_input(packet_payload.get('text', ''))
    base64_media_stream = packet_payload.get('image', '')
    
    if not target_channel or (not message_content and not base64_media_stream):
        return jsonify({"error": "Packet dropped: Structure data malformed"}), 400
        
    compiled_chat_node = {
        'room': target_channel,
        'text': message_content,
        'image': base64_media_stream,
        'sender': active_identity,
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    MEMORY_CHATS.append(compiled_chat_node)
    run_garbage_collection_sweep()
    return jsonify({"status": "success", "scope": "public_channel_dispatch"})

@app.route('/api/get_dms', methods=['GET'])
def get_dms():
    """ Queries encrypted-style direct communications between paired endpoints """
    requesting_identity = session.get('username')
    target_recipient = request.args.get('target')
    
    if not requesting_identity or not target_recipient:
        return jsonify({"error": "Incomplete query trace properties"}), 400
        
    bi_directional_hash = "-".join(sorted([requesting_identity, target_recipient]))
    private_history = [
        dm_node for dm_node in MEMORY_DMS
        if dm_node.get('dm_id') == bi_directional_hash
    ]
    return jsonify(private_history[-40:])

@app.route('/api/send_dm', methods=['POST'])
def send_dm():
    """ Locks a confidential private data node into cloud instance indexing """
    requesting_identity = session.get('username')
    if not requesting_identity:
        return jsonify({"error": "Session verification denied"}), 401
        
    packet_payload = request.get_json() or {}
    target_recipient = packet_payload.get('target')
    message_content = sanitize_user_input(packet_payload.get('text', ''))
    base64_media_stream = packet_payload.get('image', '')
    
    if not target_recipient or (not message_content and not base64_media_stream):
        return jsonify({"error": "Packet dropped: Incomplete parameters structural setup"}), 400
        
    bi_directional_hash = "-".join(sorted([requesting_identity, target_recipient]))
    
    compiled_dm_node = {
        'dm_id': bi_directional_hash,
        'text': message_content,
        'image': base64_media_stream,
        'sender': requesting_identity,
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    MEMORY_DMS.append(compiled_dm_node)
    run_garbage_collection_sweep()
    return jsonify({"status": "success", "scope": "direct_message_dispatch"})

# -------------------------------------------------------------------------
# STORIES & SNAP RECORDING API
# -------------------------------------------------------------------------
@app.route('/api/upload_story', methods=['POST'])
def upload_story():
    """ Broadcasts an image byte-array status profile node globally """
    requesting_identity = session.get('username')
    if not requesting_identity:
        return jsonify({"error": "Session verification denied"}), 401
        
    packet_payload = request.get_json() or {}
    base64_media_stream = packet_payload.get('image')
    
    if not base64_media_stream:
        return jsonify({"error": "Packet dropped: Content payload empty"}), 400
        
    compiled_story_node = {
        'username': requesting_identity,
        'image': base64_media_stream,
        'timestamp': datetime.now().strftime('%I:%M %p')
    }
    
    MEMORY_STORIES.append(compiled_story_node)
    run_garbage_collection_sweep()
    return jsonify({"status": "success", "scope": "stories_broadcast"})

# -------------------------------------------------------------------------
# ADVANCED WEBRTC CALLING & SIGNALING ROUTING ENGINE
# -------------------------------------------------------------------------
@app.route('/api/signal/post', methods=['POST'])
def post_signal():
    """ Buffers ICE candidate data streams and WebRTC connection configurations """
    requesting_identity = session.get('username')
    if not requesting_identity:
        return jsonify({"error": "Session verification denied"}), 401
        
    packet_payload = request.get_json() or {}
    target_recipient = packet_payload.get('target')
    signal_data = packet_payload.get('packet')
    transmission_type = packet_payload.get('type') # 'offer' / 'answer' / 'candidate'
    
    if not target_recipient or not transmission_type:
        return jsonify({"error": "Malformed network stream parameters"}), 400
        
    # Queue connection node to signaling matrix stack
    ACTIVE_SIGNALS[target_recipient] = {
        "from": requesting_identity,
        "packet": signal_data,
        "type": transmission_type,
        "timestamp": datetime.now().strftime('%I:%M:%S %p')
    }
    
    if transmission_type in ['offer', 'answer']:
        CALL_HISTORY_LOGS.append({
            "caller": requesting_identity,
            "receiver": target_recipient,
            "type": transmission_type,
            "time": datetime.now().strftime('%I:%M %p')
        })
        
    return jsonify({"status": "buffered", "routing_target": target_recipient})

@app.route('/api/signal/poll', methods=['GET'])
def poll_signal():
    """ Checks for real-time video/voice signaling packets waiting in line """
    requesting_identity = session.get('username')
    if not requesting_identity:
        return jsonify({"error": "Session verification denied"}), 401
        
    # Extract waiting signal data packet
    waiting_packet = ACTIVE_SIGNALS.pop(requesting_identity, {})
    return jsonify(waiting_packet)

# -------------------------------------------------------------------------
# REAL-TIME SYSTEM DIAGNOSTICS & TELEMETRY
# -------------------------------------------------------------------------
@app.route('/api/diagnostics', methods=['GET'])
def get_diagnostics():
    """ Telemetry monitoring dashboard data readout link """
    if 'username' not in session:
        return jsonify({"error": "Unauthorized endpoint trace request"}), 403
        
    diagnostic_report = {
        "engine_status": "ONLINE",
        "framework_preset": "Flask Serverless Architecture",
        "active_user_registrations": len(MEMORY_USERS),
        "total_messages_buffered": len(MEMORY_CHATS) + len(MEMORY_DMS),
        "stories_broadcasted_count": len(MEMORY_STORIES),
        "unrouted_signals_in_queue": len(ACTIVE_SIGNALS),
        "historical_call_connections": len(CALL_HISTORY_LOGS),
        "server_local_timestamp": datetime.now().isoformat()
    }
    return jsonify(diagnostic_report)

# -------------------------------------------------------------------------
# PROCESS BOOTSTRAP EXECUTOR LOOP
# -------------------------------------------------------------------------
if __name__ == '__main__':
    print("\n==================================================================")
    print("        DAPCHAT ECOSYSTEM FRAMEWORK - SERVERLESS PRESET RUNNER     ")
    print("==================================================================")
    print(" >>> Deployment Infrastructure: Optimized for Vercel Cloud Nodes")
    print(" >>> Engine Status: Production Stack Active [RAM Guard Enabled]")
    print(" >>> Core Pipeline Routing Port Allocation Target: 127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=True)