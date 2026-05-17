from flask import Flask, render_template, jsonify, request
import os
import random
import cv2
from deepface import DeepFace
import logging

app = Flask(__name__, static_folder="static", template_folder="templates")

# Base path for music files (adjusted as per your path)
MUSIC_BASE_PATH = os.path.join(app.static_folder, "songs")

# Supported emotion labels
emotion_labels = ["Angry", "Happy", "Sad", "Relaxed"]

# Map emotions to emojis for UI
emotion_emojis = {
    "Angry": "😠",
    "Happy": "😄",
    "Sad": "😢",
    "Relaxed": "😌",
    "Neutral": "🙂"  # Add a Neutral emoji
}

def get_random_song(emotion):
    emotion_folder = os.path.join(MUSIC_BASE_PATH, emotion)
    if not os.path.exists(emotion_folder):
        logging.error(f"Emotion folder {emotion} not found.")
        return None
    songs = [s for s in os.listdir(emotion_folder) if s.lower().endswith(".mp3")]
    if not songs:
        logging.error(f"No songs found for emotion {emotion}.")
    return random.choice(songs) if songs else None

def detect_emotion_from_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None, "🚫 Webcam not accessible. Please check permissions or device."

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None, "🚫 Failed to capture frame from webcam."

    try:
        # Log the frame captured
        cv2.imwrite("debug_frame.jpg", frame)
        analysis = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
        if isinstance(analysis, list):
            analysis = analysis[0]
        detected_emotion = analysis.get("dominant_emotion", "").capitalize()

        for emotion in emotion_labels:
            if detected_emotion.lower() == emotion.lower():
                return emotion, None
        
        # If no match is found, return 'Happy' for Neutral
        if detected_emotion.lower() == "neutral":
            return "Happy", None

        return None, f"🤔 Detected emotion '{detected_emotion}' is not supported."

    except Exception as e:
        logging.error(f"Emotion detection error: {str(e)}")
        return None, f"💥 Emotion detection error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_emotion', methods=['POST'])
def get_emotion():
    frame_data = request.json.get("frame")
    if not frame_data:
        return jsonify({"error": "No frame data received."})

    # Decode the frame and process it for emotion detection
    try:
        analysis = DeepFace.analyze(frame_data, actions=["emotion"], enforce_detection=False)
        if isinstance(analysis, list):
            analysis = analysis[0]
        detected_emotion = analysis.get("dominant_emotion", "").capitalize()

        for emotion in emotion_labels:
            if detected_emotion.lower() == emotion.lower():
                return jsonify({
                    "emotion": emotion,
                    "emoji": emotion_emojis.get(emotion, ""),
                })

        if detected_emotion.lower() == "neutral":
            return jsonify({
                "emotion": "Happy",
                "emoji": emotion_emojis.get("Happy", ""),
            })

        return jsonify({"error": f"🤔 Detected emotion '{detected_emotion}' is not supported."})

    except Exception as e:
        logging.error(f"Emotion detection error: {str(e)}")
        return jsonify({"error": f"💥 Emotion detection error: {str(e)}"})

@app.route('/get_emotion', methods=['GET'])
def get_emotion_webcam():
    detected_emotion, error = detect_emotion_from_webcam()
    if error:
        return jsonify({"error": error})

    song = get_random_song(detected_emotion)
    if not song:
        return jsonify({"error": f"🎵 No songs found for '{detected_emotion}' mood."})

    # Ensure the correct path is sent
    return jsonify({
        "emotion": detected_emotion,
        "emoji": emotion_emojis.get(detected_emotion, ""),
        "song": song,
        "path": f"{detected_emotion}/{song}"  # Only send the relative path
    })

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

