document.addEventListener('DOMContentLoaded', () => {
  const detectBtn = document.getElementById('detectBtn');
  const emotionBox = document.getElementById('emotionBox');
  const nowPlaying = document.getElementById('nowPlaying');
  const playPauseBtn = document.getElementById('playPauseBtn');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const volumeSlider = document.getElementById('volumeSlider');
  const audioPlayer = document.getElementById('audioPlayer');
  const themeToggle = document.getElementById('themeToggle');
  let isPlaying = false;
  let currentEmotion = '';
  let isRemote = false;
  let remoteInfo = null;
  let currentSong = 0;

  detectBtn.addEventListener('click', async () => {
    try {
      // Call the backend to detect emotion
      const response = await fetch('/get_emotion');
      const data = await response.json();

      if (data.error) {
        emotionBox.innerText = data.error;
        showToast(data.error);
      } else if (data.emotion) {
        currentEmotion = data.emotion.toLowerCase();
        const displayEmotion = currentEmotion.charAt(0).toUpperCase() + currentEmotion.slice(1);
        emotionBox.innerText = `${displayEmotion} 😃`;
        if (data.path) {
          // Remote or provided path
          isRemote = !!data.is_remote;
          remoteInfo = data;
          audioPlayer.src = data.path;
          nowPlaying.innerText = `🎵 ${data.song}${data.artist ? ' - ' + data.artist : ''}`;
          audioPlayer.play();
          isPlaying = true;
        } else {
          isRemote = false;
          remoteInfo = null;
          emotionBox.innerText = 'No remote track available for this emotion.';
          showToast('No remote track available');
        }
      } else {
        emotionBox.innerText = 'Unable to detect emotion. Please try again.';
      }
    } catch (error) {
      console.error('Error detecting emotion:', error);
      emotionBox.innerText = 'Error detecting emotion.';
    }
  });

  // Local playback removed; app uses remote API-only tracks. If remote playback
  // is not available the backend returns an error which is shown to the user.

  playPauseBtn.addEventListener('click', () => {
    if (isPlaying) {
      audioPlayer.pause();
      playPauseBtn.innerText = '▶️';
    } else {
      audioPlayer.play();
      playPauseBtn.innerText = '⏸️';
    }
    isPlaying = !isPlaying;
  });

  prevBtn.addEventListener('click', () => {
    showToast('Remote-only mode: prev not available');
  });

  nextBtn.addEventListener('click', () => {
    showToast('Remote-only mode: next not available');
  });

  volumeSlider.addEventListener('input', () => {
    audioPlayer.volume = volumeSlider.value;
  });

  themeToggle.addEventListener('change', () => {
    if (themeToggle.checked) {
      document.body.style.background = 'linear-gradient(to right, #ff7e5f, #feb47b)';
    } else {
      document.body.style.background = 'linear-gradient(to right, #00c6ff, #0072ff)';
    }
  });
});
