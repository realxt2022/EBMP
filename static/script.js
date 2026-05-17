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
  let songs = {
    'happy': ['happy1.mp3', 'happy2.m4a'],
    'sad': ['sad1.mp3', 'sad2.m4a', 'sad3.m4a', 'sad4.mp3', 'sad5.mp3', 'sad6.mp3', 'sad7.mp3'],
    'relaxed': ['neutral1.mp3', 'neutral2.mp3', 'neutral3.mp3', 'neutral4.mp3', 'neutral5.mp3', 'neutral6.mp3'],
    'angry': ['angry1.mp3', 'angry2.mp3']
  };
  let currentSong = 0;

  detectBtn.addEventListener('click', async () => {
    try {
      // Call the backend to detect emotion
      const response = await fetch('/get_emotion');
      const data = await response.json();

      if (data.emotion) {
        currentEmotion = data.emotion.toLowerCase();
        const displayEmotion = currentEmotion.charAt(0).toUpperCase() + currentEmotion.slice(1);
        emotionBox.innerText = `${displayEmotion} 😃`;
        playSong(currentEmotion);
      } else {
        emotionBox.innerText = 'Unable to detect emotion. Please try again.';
      }
    } catch (error) {
      console.error('Error detecting emotion:', error);
      emotionBox.innerText = 'Error detecting emotion.';
    }
  });

  function playSong(emotion) {
    const songList = songs[emotion];
    if (!songList || songList.length === 0) {
      emotionBox.innerText = 'No songs found for this emotion.';
      return;
    }

    currentSong = 0; // Reset to first song of the emotion
    audioPlayer.src = `/static/songs/${emotion}/${songList[currentSong]}`;
    nowPlaying.innerText = `🎵 ${songList[currentSong]}`;
    audioPlayer.play();
    isPlaying = true;
  }

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
    if (currentSong > 0) {
      currentSong--;
      audioPlayer.src = `/static/songs/${currentEmotion}/${songs[currentEmotion][currentSong]}`;
      nowPlaying.innerText = `🎵 ${songs[currentEmotion][currentSong]}`;
      audioPlayer.play();
    }
  });

  nextBtn.addEventListener('click', () => {
    if (currentSong < songs[currentEmotion].length - 1) {
      currentSong++;
      audioPlayer.src = `/static/songs/${currentEmotion}/${songs[currentEmotion][currentSong]}`;
      nowPlaying.innerText = `🎵 ${songs[currentEmotion][currentSong]}`;
      audioPlayer.play();
    }
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
