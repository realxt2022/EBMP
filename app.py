from flask import Flask, render_template, jsonify, request, send_from_directory
import base64
import os
import random
import cv2
import numpy as np
from deepface import DeepFace
import logging
from ytmusicapi import YTMusic

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning('python-dotenv not installed; relying on environment variables only')

app = Flask(__name__, static_folder="static", template_folder="templates")
MUSIC_BASE_PATH = os.path.join(app.static_folder, 'songs')

# Public YouTube Music mode only; no OAuth, no account login, no oauth.json.
try:
    yt = YTMusic()
    logging.info('YTMusic initialized in public mode')
except Exception as e:
    logging.error('YTMusic initialization failed in public mode: %s', e)
    yt = None

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

def fetch_remote_tracks_from_ytmusic(emotion):
    if yt is None:
        return None, 'YTMusic is not initialized in public mode. Ensure internet access and that YTMusic public search is supported.'

    mood = emotion.lower()
    search_phrases = [
        f'new gen {mood} hindi english',
        f'new {mood} hindi english',
        f'{mood} hindi english',
        f'{mood} english pop',
        f'{mood} hindi pop',
        f'{mood} rap hindi english',
        f'{mood} pop hindi english',
        f'new {mood} pop',
        f'new {mood} rap',
        f'{mood} english r&b',
        f'{mood} hindi hip hop',
        f'new {mood} indie hindi english',
    ]
    random.shuffle(search_phrases)

    try:
        tracks = []
        last_query = None

        for phrase in search_phrases:
            last_query = phrase
            logging.info('YTMusic search query=%s', phrase)
            search_results = yt.search(phrase, filter='songs', limit=50)
            if not search_results:
                continue

            for item in search_results:
                video_id = item.get('videoId')
                if not video_id:
                    continue
                artist = 'Unknown Artist'
                if item.get('artists'):
                    artist = item['artists'][0].get('name', artist)
                elif item.get('subtitle'):
                    artist = item.get('subtitle')
                tracks.append({
                    'title': item.get('title') or 'Unknown Title',
                    'artist': artist,
                    'videoId': video_id,
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'musicUrl': f'https://music.youtube.com/watch?v={video_id}'
                })
                if len(tracks) >= 20:
                    break
            if tracks:
                logging.info('YTMusic returned %s tracks for query=%s', len(tracks), phrase)
                break

        if not tracks:
            error_msg = f"YTMusic returned zero results for this mood. Last query: {last_query}"
            logging.info(error_msg)
            return None, error_msg

        random.shuffle(tracks)
        return tracks, None
    except Exception as e:
        error_msg = f"YTMusic fetch failed: {e}"
        logging.warning(error_msg)
        return None, error_msg


def fetch_local_tracks(emotion):
    emotion_to_folder = {
        'happy': 'happy',
        'sad': 'sad',
        'angry': 'angry',
        'relaxed': 'neutral',
        'neutral': 'neutral',
    }
    folder_name = emotion_to_folder.get(emotion.lower(), emotion.lower())
    folder_path = os.path.join(MUSIC_BASE_PATH, folder_name)
    search_paths = [folder_path] if os.path.isdir(folder_path) else [MUSIC_BASE_PATH]

    valid_audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}
    tracks = []

    for search_path in search_paths:
        for root, _, files in os.walk(search_path):
            for filename in files:
                _, ext = os.path.splitext(filename)
                if ext.lower() not in valid_audio_extensions:
                    continue
                track_path = os.path.join(root, filename)
                rel_path = os.path.relpath(track_path, app.static_folder).replace('\\', '/')
                tracks.append({
                    'title': os.path.splitext(filename)[0],
                    'artist': folder_name,
                    'url': f'/static/{rel_path}',
                })
                if len(tracks) >= 20:
                    break
            if len(tracks) >= 20:
                break
        if tracks:
            break

    if not tracks:
        return None, 'No local songs found for this mood.'

    random.shuffle(tracks)
    return tracks, None


def normalize_detected_emotion(detected_emotion):
    if not detected_emotion or not isinstance(detected_emotion, str):
        return None

    emotion_key = detected_emotion.strip().lower()
    mapping = {
        'happy': 'Happy',
        'joy': 'Happy',
        'joyful': 'Happy',
        'surprise': 'Happy',
        'surprised': 'Happy',
        'sad': 'Sad',
        'sadness': 'Sad',
        'angry': 'Angry',
        'anger': 'Angry',
        'disgust': 'Angry',
        'contempt': 'Angry',
        'fear': 'Sad',
        'neutral': 'Relaxed',
        'relaxed': 'Relaxed',
        'calm': 'Relaxed',
        'serene': 'Relaxed',
    }

    if emotion_key in mapping:
        return mapping[emotion_key]

    if 'angry' in emotion_key or 'anger' in emotion_key or 'disgust' in emotion_key or 'contempt' in emotion_key:
        return 'Angry'
    if 'sad' in emotion_key or 'fear' in emotion_key:
        return 'Sad'
    if 'happy' in emotion_key or 'joy' in emotion_key or 'surprise' in emotion_key:
        return 'Happy'
    if 'neutral' in emotion_key or 'relax' in emotion_key or 'calm' in emotion_key or 'serene' in emotion_key:
        return 'Relaxed'

    return None

def get_random_song(emotion):
    logging.info('Attempting remote search using YTMusic public mode')
    remote, remote_error = fetch_remote_tracks_from_ytmusic(emotion) if yt is not None else (None, 'YTMusic is not initialized in public mode. Ensure internet access and that the public search API is available.')
    if remote:
        logging.info('Using remote playlist from YTMusic with %s tracks', len(remote))
        return remote, True, None

    logging.error('Remote music fetch failed: %s', remote_error)
    return None, True, remote_error or 'Remote music fetch failed. Please check internet connectivity and YTMusic public search availability.'
def decode_frame_data(frame_data):
    if not frame_data or not isinstance(frame_data, str):
        return None, 'Invalid frame payload.'

    if ',' not in frame_data:
        return None, 'Frame data is not a valid data URL.'

    try:
        header, encoded = frame_data.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return None, 'Unable to decode image from frame data.'
        return img, None
    except Exception as e:
        return None, f'Error decoding frame data: {e}'

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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.svg', mimetype='image/svg+xml')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_emotion', methods=['POST'])
def get_emotion():
    frame_data = request.json.get("frame")
    if not frame_data:
        return jsonify({"error": "No frame data received."})

    image, decode_error = decode_frame_data(frame_data)
    if decode_error:
        return jsonify({"error": decode_error})

    try:
        analysis = DeepFace.analyze(image, actions=["emotion"], enforce_detection=False)
        if isinstance(analysis, list):
            analysis = analysis[0]
        detected_emotion = analysis.get("dominant_emotion", "").capitalize()
        normalized_emotion = normalize_detected_emotion(detected_emotion)

        logging.info('DeepFace detected emotion=%s normalized=%s', detected_emotion, normalized_emotion)

        if normalized_emotion:
            tracks, is_remote, error = get_random_song(normalized_emotion)
            if tracks is None:
                return jsonify({"error": error})

            return jsonify({
                "emotion": normalized_emotion,
                "emoji": emotion_emojis.get(normalized_emotion, ""),
                "song": tracks[0].get('title'),
                "artist": tracks[0].get('artist'),
                "path": tracks[0].get('url'),
                "tracks": tracks,
                "is_remote": is_remote,
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

    normalized_emotion = normalize_detected_emotion(detected_emotion)
    logging.info('DeepFace detected emotion=%s normalized=%s', detected_emotion, normalized_emotion)

    if not normalized_emotion:
        return jsonify({"error": f"🤔 Detected emotion '{detected_emotion}' is not supported."})

    tracks, is_remote, error = get_random_song(normalized_emotion)
    if tracks is None:
        return jsonify({"error": error})

    return jsonify({
        "emotion": normalized_emotion,
        "emoji": emotion_emojis.get(normalized_emotion, ""),
        "song": tracks[0].get('title'),
        "artist": tracks[0].get('artist'),
        "path": tracks[0].get('url'),
        "tracks": tracks,
        "is_remote": is_remote,
    })

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

