const fs = require('fs');
const ytdl = require('ytdl-core');

const api_data = require('./sample.json');

const videoURL = String(api_data);
const outputFilePath = 'downloaded/video.mp4';

const audio = ytdl(videoURL, { quality: 'highestaudio' })

audio.on('end', function() {
    console.log("Video has been downloaded completely")
  });
  
  audio.pipe(fs.createWriteStream(outputFilePath));