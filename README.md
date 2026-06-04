# Emotion-Based Music Player (EBMP)

An emotion-driven web application that detects facial expressions and recommends music based on the user's mood. The app uses a webcam feed, machine learning emotion recognition, and either local song files or YouTube Music search results to create a personalized listening experience.

## Features

- Facial emotion detection via webcam
- Mood-based music recommendation and playback
- Local audio library support in `static/songs/`
- Public YouTube Music search fallback using `ytmusicapi`
- Dynamic UI behavior based on detected emotion
- Theme toggle and responsive layout

## Supported Emotions

- Angry
- Happy
- Sad
- Relaxed
- Neutral

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/EBMP.git
   cd EBMP
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Add environment variables in a `.env` file if needed.

## Running the App

Start the Flask application:

```bash
python app.py
```

Then open your browser at `http://127.0.0.1:5000`.

## Project Structure

- `app.py` - Flask backend and emotion detection logic
- `templates/index.html` - Main UI page
- `static/styles.css` - CSS styling
- `static/script.js` - Frontend logic and audio controls
- `static/songs/` - Local song folders for moods
- `requirements.txt` - Python dependencies
- `Emotion_Detection.h5`, `emotion_model.hdf5` - emotion model files

## Dependencies

The app relies on:

- Flask
- gunicorn
- deepface
- tensorflow
- keras
- opencv-python-headless
- numpy
- ytmusicapi
- python-dotenv

## Notes

- The app attempts to use YouTube Music public mode for remote track search.
- If no remote tracks are available, it can fall back to local songs in `static/songs/`.
- Make sure your webcam is accessible and your browser allows camera access.

## Future Enhancements

- Add more emotion categories
- Support custom user playlists
- Provide continuous real-time mood tracking
- Build a mobile-friendly version

## License

This project does not include a license file. Add one if you want to share or distribute the code.
