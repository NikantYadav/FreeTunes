const ytdl = require('ytdl-core');
const fs = require('fs');
const path = require('path');

// Replace this with the URL of the YouTube video you want to download
const videoURL = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'; // Example URL
const output = path.resolve(__dirname, 'video.mp4'); // Output file path

ytdl(videoURL)
  .pipe(fs.createWriteStream(output))
  .on('finish', () => {
    console.log('Download complete!');
  })
  .on('error', (err) => {
    console.error('Error:', err);
  });
