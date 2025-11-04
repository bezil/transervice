from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
from gtts import gTTS
from flask_apscheduler import APScheduler
import uuid
import os
import time

app = Flask(__name__)
translator = Translator()
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Allow CORS from a specific domain (replace with your desired domain)
CORS(app, resources={r"/*": {"origins": [
    "https://live.devbez.digital",
    "https://spiral-wool-angle.glitch.me",
    "https://translate.uicaster.com"
]}})

# Disable debug mode and set secret key for production
# app.config['DEBUG'] = False
# app.config['SECRET_KEY'] = 'your-secret-key'

# Path to save the generated TTS audio files
AUDIO_DIR = "static/translations"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.route('/translate', methods=['POST'])
def translate_text():
    # Parse JSON input
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Get text and code from the request
    text = data.get("text")
    code = data.get("code")

    # Validate input
    if not text:
        return jsonify({"error": "No text provided"}), 400
    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        # Generate a unique filename for this translation
        unique_filename = f"{uuid.uuid4()}.mp3"
        audio_file_path = os.path.join(AUDIO_DIR, unique_filename)
        
        # Translate text to the selected language
        translated = translator.translate(text, dest=code)
        # Generate speech from translated text
        tts = gTTS(translated.text, lang=code)
        tts.save(audio_file_path)

        return jsonify({
            "translated_text": translated.text,
            "audio_path": audio_file_path,
            "audio_filename": unique_filename            
        })
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

@scheduler.task('interval', id='cleanup_old_audio', hours=1)
def cleanup_audio():
    try:
        current_time = time.time()
        for filename in os.listdir(AUDIO_DIR):
            file_path = os.path.join(AUDIO_DIR, filename)
            if os.path.isfile(file_path):
                if current_time - os.path.getctime(file_path) > 3600:
                    os.unlink(file_path)
        print(f"Cleanup completed at {time.ctime()}")
    except Exception as e:
        print(f"Cleanup failed: {str(e)}")

# comment below for prod
# if __name__ == '__main__':
#     app.run(debug=True)
