import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import subprocess
from flask_cors import CORS  # Enable cross-origin requests

app = Flask(__name__)
CORS(app)  # Allow frontend requests

UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_music', methods=['POST'])
def upload_music():
    if 'music_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['music_file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Check if file already exists
        if os.path.exists(file_path):
            message = 'File already exists. Playing existing file.'
        else:
            file.save(file_path)
            message = 'Music uploaded and playing!'

        # Play the file using `aplay`
        try:
            subprocess.run(["aplay", file_path], check=True)
            return jsonify({'message': message, 'file': filename}), 200
        except subprocess.CalledProcessError:
            return jsonify({'error': 'File found but failed to play'}), 500

    return jsonify({'error': 'Invalid file type. Only .wav allowed'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6970, debug=True)
