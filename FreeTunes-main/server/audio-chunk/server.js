const express = require('express');
const ytdl = require('ytdl-core');
const app = express();
const port = 3000;

app.get('/video', (req, res) => {
  const videoUrl = 'http://www.youtube.com/watch?v=aqz-KE-bpKQ'; // Replace with the desired YouTube URL

  console.log('Received request for video stream');
  console.log('Video URL:', videoUrl);

  // Set headers to properly handle video content
  res.setHeader('Content-Type', 'video/mp4');
  res.setHeader('Content-Disposition', 'inline; filename="video.mp4"');

  // Start streaming video
  ytdl(videoUrl, { filter: 'audioandvideo' })
    .on('response', (response) => {
      console.log('Received response from YouTube:', response.statusCode);
      console.log('Response headers:', response.headers);
    })
    .on('error', (error) => {
      console.error('Error occurred while streaming video:', error);
      res.status(500).send('Error occurred while streaming video');
    })
    .on('progress', (chunkLength, downloaded, total) => {
      console.log(`Progress: ${Math.round((downloaded / total) * 100)}% (${downloaded} bytes of ${total} bytes)`);
    })
    .pipe(res)
    .on('finish', () => {
      console.log('Streaming finished successfully');
    });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
