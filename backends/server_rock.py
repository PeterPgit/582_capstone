# Authors: Ian Wilson, Andrew Uriell, Peter Pharm, Michael Oliver
# Class: Senior Design -- EECS582
# Date: April 10, 2025
# Purpose: Python3 secure Flask server to upload & play music
# Code sources: Stackoverflow, ChatGPT, ourselves

import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import subprocess
from flask_cors import CORS
from functools import wraps

# --- CONFIG ---
UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
ALLOWED_EXTENSIONS = {'wav'}
AUTH_TOKEN = "super_secret_token"
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

# --- APP SETUP ---
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes (adjust as needed)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- HELPERS ---
# Only allows WAV files to be played
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Handles auth of the web requests
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f"Bearer {AUTH_TOKEN}":
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# --- ROUTES ---
@app.route('/upload_music', methods=['POST'])
@require_auth
# Checks the web request and plays the file if it already exists, or uploads the file to the server and then plays the music
def upload_music():
    if 'music_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['music_file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(file_path):
            message = 'File already exists. Playing existing file.'
        else:
            file.save(file_path)
            message = 'Music uploaded and playing!'

        try:
            subprocess.run(["aplay", file_path], check=True)
            return jsonify({'message': message, 'file': filename}), 200
        except subprocess.CalledProcessError:
            return jsonify({'error': 'File found but failed to play'}), 500

    return jsonify({'error': 'Invalid file type. Only .wav allowed'}), 400

# --- MAIN ---
if __name__ == '__main__':
    context = (CERT_FILE, KEY_FILE)  # Certificate & key files for HTTPS
    app.run(host='0.0.0.0', port=6970, ssl_context=context)

